from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import shuffle
from collections import defaultdict
from bson.objectid import ObjectId

from apscheduler.schedulers.base import JobLookupError

from flask_babel import gettext
from flask import render_template, redirect, url_for, jsonify, request, session
from flask_login import logout_user, login_required, current_user

import app.constants as constants
import app.utils as utils
from app import exchange, scheduler
from app.user import user
from app.home.user_loging_manager import MoneyEntry, Settings, DateRange, User

from .forms import MoneyEntryForm

AVAILABLE_CURRENCIES_FOR_COMBO = ','.join("%s" % currency for currency in constants.AVAILABLE_CURRENCIES)


class GraphNode(object):
    def __init__(self, incomes=0.00, expenses=0.00):
        self.incomes = incomes
        self.expenses = expenses

    expenses = float
    incomes = float


def _remove_from_scheduler(mid: str):
    try:
        scheduler.remove_job(job_id=mid)
    except JobLookupError:
        return


def _add_to_scheduler(uid: ObjectId, mid: str, date: datetime):
    scheduler.add_job(recurring, 'date', run_date=date, id=mid, args=[uid, mid])


def relativedelta_from_recurring(rec: MoneyEntry.Recurring):
    if rec == MoneyEntry.Recurring.EVERY_DAY:
        return relativedelta(days=1)
    elif rec == MoneyEntry.Recurring.EVERY_MONTH:
        return relativedelta(months=1)
    elif rec == MoneyEntry.Recurring.EVERY_YEAR:
        return relativedelta(years=1)
    else:
        return None


def recurring(uid: ObjectId, mid: str):
    us = User.objects(id=uid).first()
    if not us:
        return

    for entry in us.entries:
        if str(entry.id) == mid:
            if not entry.is_recurring():
                return

            cloned = entry.clone()
            date = datetime.now()
            cloned.date = utils.stable_date(date)

            add_entry(us, cloned)
            return


def add_entry(us: User, entry: MoneyEntry):
    us.entries.append(entry)
    us.save()

    rel = relativedelta_from_recurring(entry.recurring)
    if not rel:
        return

    date = entry.date + rel
    mid = str(entry.id)
    _add_to_scheduler(us.id, mid, date)


def edit_entry(us: User, entry: MoneyEntry):
    entry.save()

    mid = str(entry.id)
    _remove_from_scheduler(mid)

    rel = relativedelta_from_recurring(entry.recurring)
    if not rel:
        return

    date = entry.date + rel
    _add_to_scheduler(us.id, mid, date)


def remove_entry(us: User, mid: str):
    for entry in current_user.entries:
        if str(entry.id) == mid:
            us.entries.remove(entry)
            us.save()
            break

    _remove_from_scheduler(mid)


def exchange_currency(base: str, to: str, amount: float) -> float:
    if base == to:
        return amount

    json = exchange.get_rates(base)
    if not json:
        return 0.00

    rates = json[to]
    return amount * rates


def add_money_entry(method: str, entry_type: MoneyEntry.Type, locale: str):
    if entry_type == MoneyEntry.Type.INCOME:
        categories = current_user.incomes_categories
    elif entry_type == MoneyEntry.Type.EXPENSE:
        categories = current_user.expenses_categories
    else:
        categories = []

    extended_cat = []
    for index, value in enumerate(categories):
        extended_cat.append((index, value))

    form = MoneyEntryForm(categories=extended_cat, type=entry_type)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        add_entry(current_user, new_entry)
        return jsonify(status='ok'), 200

    return render_template('user/money/add.html', form=form, locale=locale,
                           available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO)


def edit_money_entry(method: str, entry: MoneyEntry, categories: list, locale: str):
    extended_cat = []
    category_index = 0
    for index, value in enumerate(categories):
        extended_cat.append((index, value))
        if entry.category == value:
            category_index = index

    form = MoneyEntryForm(categories=extended_cat, obj=entry)
    if method == 'GET':
        form.category.data = category_index

    if method == 'POST' and form.validate_on_submit():
        entry = form.update_entry(entry)
        edit_entry(current_user, entry)
        return jsonify(status='ok'), 200

    return render_template('user/money/edit.html', form=form, locale=locale,
                           available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO)


def render_details(title: str, data_dict: defaultdict(float), total: float):
    labels = []
    data = []
    for key, value in data_dict.items():
        labels.append(key)
        r = constants.round_value(value / total)
        data.append(r)

    colors = list(constants.AVAILIBLE_CHART_COLORS)
    shuffle(colors)
    return render_template('user/details.html', title=title, labels=labels, data=data,
                           colors=colors[:len(data)])


def get_settings():
    rsettings = current_user.settings
    locale = rsettings.locale
    currency = rsettings.currency
    start_date = rsettings.date_range.start_date
    end_date = rsettings.date_range.end_date
    return currency, locale, start_date, end_date


def get_runtime_settings():
    rsettings = current_user.settings
    if session.get('currency'):
        currency = session['currency']
    else:
        currency = rsettings.currency

    locale = rsettings.locale
    if session.get('date_range'):
        start_date = rsettings.date_range.start_date
        end_date = rsettings.date_range.end_date
    else:
        start_date = rsettings.date_range.start_date
        end_date = rsettings.date_range.end_date

    return currency, locale, start_date, end_date


# routes
@user.route('/dashboard')
@login_required
def dashboard():
    incomes = []
    expenses = []
    total = 0.00
    graph_dict = defaultdict(GraphNode)

    currency, locale, start_date, end_date = get_runtime_settings()

    for entry in current_user.entries:
        entry_date = entry.date
        entry_date_min, entry_date_max = utils.year_month_date(entry_date)
        entry_val = exchange_currency(entry.currency, currency, entry.value)

        if entry.type == MoneyEntry.Type.INCOME:
            if (start_date <= entry_date) and (entry_date <= end_date):
                total += entry_val
                incomes.append(entry)

            graph_dict[entry_date_max].incomes += entry_val
        elif entry.type == MoneyEntry.Type.EXPENSE:
            if (start_date <= entry_date) and (entry_date <= end_date):
                total -= entry_val
                expenses.append(entry)

            graph_dict[entry_date_max].expenses += entry_val

    chart_labels = []
    chart_incomes = []
    chart_expenses = []
    for key, value in sorted(graph_dict.items()):
        chart_labels.append(key.strftime('%B %Y'))
        rounded_incomes = constants.round_value(value.incomes)
        chart_incomes.append(rounded_incomes)
        rounded_expenses = constants.round_value(value.expenses)
        chart_expenses.append(rounded_expenses)

    rounded_total = constants.round_value(total)
    start_date_str = start_date.strftime(constants.DATE_JS_FORMAT)
    end_date_str = end_date.strftime(constants.DATE_JS_FORMAT)

    return render_template('user/dashboard.html', total=rounded_total, incomes=incomes, expenses=expenses,
                           start_date=start_date_str, end_date=end_date_str, locale=locale,  # for date range
                           currency=currency, available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO,  # for total balance
                           chart_labels=chart_labels, chart_incomes=chart_incomes, chart_expenses=chart_expenses)


@user.route('/settings')
@login_required
def settings():
    currency, locale, start_date, end_date = get_settings()
    start_date_str = start_date.strftime(constants.DATE_JS_FORMAT)
    end_date_str = end_date.strftime(constants.DATE_JS_FORMAT)
    return render_template('user/settings.html', locale=locale,
                           available_locales=constants.AVAILABLE_LOCALES, currency=currency,
                           available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO, start_date=start_date_str,
                           end_date=end_date_str)


@user.route('/settings/apply', methods=['POST'])
@login_required
def settings_apply():
    currency = request.form['currency']
    locale = request.form['locale']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    date_range = DateRange(datetime.strptime(start_date, constants.DATE_JS_FORMAT),
                           datetime.strptime(end_date, constants.DATE_JS_FORMAT))
    current_user.settings = Settings(currency=currency, locale=locale, date_range=date_range)
    current_user.save()
    response = {}
    return jsonify(response), 200


@user.route('/runtime_settings/apply_currency', methods=['POST'])
@login_required
def runtime_settings():
    session['currency'] = request.form['currency']
    response = {}
    return jsonify(response), 200


@user.route('/logout')
@login_required
def logout():
    session.pop('currency', None)
    logout_user()
    return redirect(url_for('home.start'))


# income
@user.route('/income/details', methods=['GET'])
@login_required
def details_income():
    data_dict = defaultdict(float)
    total = 0.00

    currency, locale, start_date, end_date = get_runtime_settings()
    for entry in current_user.entries:
        entry_date = entry.date
        if entry.type == MoneyEntry.Type.INCOME:
            if (start_date <= entry_date) and (entry_date <= end_date):
                val = exchange_currency(entry.currency, currency, entry.value)
                data_dict[entry.category] += val
                total += val

    return render_details(gettext(u'Income details'), data_dict, total)


@user.route('/income/add', methods=['GET', 'POST'])
@login_required
def add_income():
    currency, locale, start_date, end_date = get_runtime_settings()
    return add_money_entry(request.method, MoneyEntry.Type.INCOME, locale)


@user.route('/income/edit/<mid>', methods=['GET', 'POST'])
@login_required
def edit_income(mid):
    for entry in current_user.entries:
        if str(entry.id) == mid:
            currency, locale, start_date, end_date = get_runtime_settings()
            return edit_money_entry(request.method, entry, current_user.incomes_categories, locale)

    responce = {"status": "failed"}
    return jsonify(responce), 404


@user.route('/income/remove', methods=['POST'])
@login_required
def remove_income():
    income_id = request.form['income_id']
    remove_entry(current_user, income_id)
    response = {"income_id": income_id}
    return jsonify(response), 200


@user.route('/income/add_category', methods=['POST'])
@login_required
def add_category_income():
    category = request.form['category']
    current_user.incomes_categories.append(category)
    current_user.save()

    response = {}
    return jsonify(response), 200


@user.route('/income/remove_category', methods=['POST'])
@login_required
def remove_category_income():
    category = request.form['category']
    current_user.incomes_categories.remove(category)
    current_user.save()

    response = {}
    return jsonify(response), 200


# expense
@user.route('/expense/details', methods=['GET'])
@login_required
def details_expense():
    data_dict = defaultdict(float)
    total = 0.00

    currency, locale, start_date, end_date = get_runtime_settings()
    for entry in current_user.entries:
        entry_date = entry.date
        if entry.type == MoneyEntry.Type.EXPENSE:
            if (start_date <= entry_date) and (entry_date <= end_date):
                val = exchange_currency(entry.currency, currency, entry.value)
                data_dict[entry.category] += val
                total += val

    return render_details(gettext(u'Expense details'), data_dict, total)


@user.route('/expense/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    currency, locale, start_date, end_date = get_runtime_settings()
    return add_money_entry(request.method, MoneyEntry.Type.EXPENSE, locale)


@user.route('/expense/edit/<mid>', methods=['GET', 'POST'])
@login_required
def edit_expense(mid):
    for entry in current_user.entries:
        if str(entry.id) == mid:
            currency, locale, start_date, end_date = get_runtime_settings()
            return edit_money_entry(request.method, entry, current_user.expenses_categories, locale)

    responce = {"status": "failed"}
    return jsonify(responce), 404


@user.route('/expense/remove', methods=['POST'])
@login_required
def remove_expense():
    expense_id = request.form['expense_id']
    remove_entry(current_user, expense_id)
    response = {"expense_id": expense_id}
    return jsonify(response), 200


@user.route('/expense/add_category', methods=['POST'])
@login_required
def add_category_expense():
    category = request.form['category']
    current_user.expenses_categories.append(category)
    current_user.save()

    response = {}
    return jsonify(response), 200


@user.route('/expense/remove_category', methods=['POST'])
@login_required
def remove_category_expense():
    category = request.form['category']
    current_user.expenses_categories.remove(category)
    current_user.save()

    response = {}
    return jsonify(response), 200
