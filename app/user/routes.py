from datetime import datetime
from dateutil.relativedelta import relativedelta
from random import shuffle
from collections import defaultdict
from bson.objectid import ObjectId

from flask import render_template, redirect, url_for, jsonify, request, session
from flask_login import logout_user, login_required, current_user

import app.constants as constants
import app.utils as utils
from app import exchange_client, scheduler
from app.user import user
from app.home.user_loging_manager import MoneyEntry, Settings, Language, DateRange, User

from .forms import MoneyEntryForm

AVAILABLE_CURRENCIES_FOR_COMBO = ','.join("%s" % currency for currency in constants.AVAILABLE_CURRENCIES)


def round_value(value: float):
    precision = 2
    return round(value, precision)


def _remove_from_scheduler(mid: str):
    try:
        scheduler.remove_job(job_id=mid)
    except Exception:
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


def exchange(base: str, to: str, amount: float) -> float:
    json = exchange_client.get_rates(base)
    if not json:
        return 0.00

    rates = json[to]
    return amount * rates


def add_money_entry(method: str, entry_type: MoneyEntry.Type, language: Language):
    if entry_type == MoneyEntry.Type.INCOME:
        categories = current_user.incomes_categories
    elif entry_type == MoneyEntry.Type.EXPENSE:
        categories = current_user.expenses_categories

    extended_cat = []
    for index, value in enumerate(categories):
        extended_cat.append((index, value))

    form = MoneyEntryForm(categories=extended_cat, type=entry_type)
    if method == 'POST' and form.validate_on_submit():
        new_entry = form.make_entry()
        add_entry(current_user, new_entry)
        return jsonify(status='ok'), 200

    return render_template('user/money/add.html', form=form, language=language,
                           available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO)


def edit_money_entry(method: str, entry: MoneyEntry, categories: list, language: Language):
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

    return render_template('user/money/edit.html', form=form, language=language,
                           available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO)


class GraphNode(object):
    def __init__(self, incomes=0.00, expenses=0.00):
        self.incomes = incomes
        self.expenses = expenses

    expenses = float
    incomes = float


def render_details(title: str, currency: str, entries: list):
    data_dict = defaultdict(float)
    total = 0.00

    for rev in entries:
        if rev.currency == currency:
            val = rev.value
        else:
            val = exchange(rev.currency, currency, rev.value)

        data_dict[rev.category] += val
        total += val

    labels = []
    data = []
    for key, value in data_dict.items():
        labels.append(key)
        r = round_value(value / total)
        data.append(r)

    colors = list(constants.AVAILIBLE_CHART_COLORS)
    shuffle(colors)
    return render_template('user/details.html', title=title, labels=labels, data=data,
                           colors=colors[:len(data)])


# routes
@user.route('/dashboard')
@login_required
def dashboard():
    incomes = []
    expenses = []
    total = 0.00
    rsettings = current_user.settings
    if session.get('currency'):
        currency = session['currency']
    else:
        currency = rsettings.currency
    language = rsettings.language
    graph_dict = defaultdict(GraphNode)
    if session.get('date_range'):
        start_date = rsettings.date_range.start_date
        end_date = rsettings.date_range.end_date
    else:
        start_date = rsettings.date_range.start_date
        end_date = rsettings.date_range.end_date

    for entry in current_user.entries:
        entry_date = entry.date
        entry_date_min, entry_date_max = utils.year_month_date(entry_date)
        if entry.currency == currency:
            entry_val = entry.value
        else:
            entry_val = exchange(entry.currency, currency, entry.value)

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
        rounded_incomes = round_value(value.incomes)
        chart_incomes.append(rounded_incomes)
        rounded_expenses = round_value(value.expenses)
        chart_expenses.append(rounded_expenses)

    rounded_total = round_value(total)
    start_date_str = start_date.strftime(constants.DATE_JS_FORMAT)
    end_date_str = end_date.strftime(constants.DATE_JS_FORMAT)

    return render_template('user/dashboard.html', total=rounded_total, incomes=incomes, expenses=expenses,
                           start_date=start_date_str, end_date=end_date_str, language=language,  # for date range
                           currency=currency, available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO,  # for total balance
                           chart_labels=chart_labels, chart_incomes=chart_incomes, chart_expenses=chart_expenses)


@user.route('/settings')
@login_required
def settings():
    rsettings = current_user.settings
    language = rsettings.language
    currency = rsettings.currency
    start_date_str = rsettings.date_range.start_date.strftime(constants.DATE_JS_FORMAT)
    end_date_str = rsettings.date_range.end_date.strftime(constants.DATE_JS_FORMAT)
    return render_template('user/settings.html', language=language,
                           available_languages=constants.AVAILABLE_LANGUAGES, currency=currency,
                           available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO, start_date=start_date_str,
                           end_date=end_date_str)


@user.route('/settings/apply', methods=['POST'])
@login_required
def settings_apply():
    currency = request.form['currency']
    language = request.form['language']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    lang = constants.get_language_by_name(language)
    dblang = Language(lang.language(), lang.locale())
    date_range = DateRange(datetime.strptime(start_date, constants.DATE_JS_FORMAT),
                           datetime.strptime(end_date, constants.DATE_JS_FORMAT))
    current_user.settings = Settings(currency=currency, language=dblang, date_range=date_range)
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
    currency = current_user.settings.currency
    return render_details('Income details', currency, current_user.incomes)


@user.route('/income/add', methods=['GET', 'POST'])
@login_required
def add_income():
    rsettings = current_user.settings
    language = rsettings.language
    return add_money_entry(request.method, MoneyEntry.Type.INCOME, language)


@user.route('/income/edit/<mid>', methods=['GET', 'POST'])
@login_required
def edit_income(mid):
    for entry in current_user.entries:
        if str(entry.id) == mid:
            rsettings = current_user.settings
            language = rsettings.language
            return edit_money_entry(request.method, entry, current_user.incomes_categories, language)

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
    currency = current_user.settings.currency
    return render_details('Expense details', currency, current_user.expenses)


@user.route('/expense/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    rsettings = current_user.settings
    language = rsettings.language
    return add_money_entry(request.method, MoneyEntry.Type.EXPENSE, language)


@user.route('/expense/edit/<mid>', methods=['GET', 'POST'])
@login_required
def edit_expense(mid):
    for entry in current_user.entries:
        if str(entry.id) == mid:
            rsettings = current_user.settings
            language = rsettings.language
            return edit_money_entry(request.method, entry, current_user.expenses_categories, language)

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
