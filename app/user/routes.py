from random import shuffle
from collections import defaultdict

from flask_babel import gettext
from flask import render_template, redirect, url_for, jsonify, request, session
from flask_login import logout_user, login_required, current_user

import app.constants as constants
import app.utils as utils
from app import exchange
from app.user import user
from app.home.money_entry import MoneyEntry

from .forms import MoneyEntryForm, SettingsForm
from .entry_scheduler import add_entry, remove_entry, edit_entry

AVAILABLE_CURRENCIES_FOR_COMBO = ','.join("%s" % currency for currency in constants.AVAILABLE_CURRENCIES)


class GraphNode(object):
    def __init__(self, incomes=0.00, expenses=0.00):
        self.incomes = incomes
        self.expenses = expenses

    expenses = float
    incomes = float


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


def get_runtime_settings():
    rsettings = current_user.settings
    if session.get('currency'):
        currency = session['currency']
    else:
        currency = rsettings.currency

    locale = rsettings.locale
    if session.get('date_range'):
        start_date = rsettings.start_date
        end_date = rsettings.end_date
    else:
        start_date = rsettings.start_date
        end_date = rsettings.end_date

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
        chart_incomes.append(value.incomes)
        chart_expenses.append(value.expenses)

    start_date_str = start_date.strftime(constants.DATE_JS_FORMAT)
    end_date_str = end_date.strftime(constants.DATE_JS_FORMAT)

    return render_template('user/dashboard.html', total=total, incomes=incomes, expenses=expenses,
                           start_date=start_date_str, end_date=end_date_str, locale=locale,  # for date range
                           currency=currency, available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO,  # for total balance
                           chart_labels=chart_labels, chart_incomes=chart_incomes, chart_expenses=chart_expenses)


@user.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(obj=current_user.settings)
    if request.method == 'POST':
        if form.validate_on_submit():
            form.update_settings(current_user.settings)
            current_user.save()
            return render_template('user/settings.html', form=form, available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO)

    return render_template('user/settings.html', form=form, available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO)


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


# flow
def render_flow(title: str, income_dict: defaultdict(float), expense_dict: defaultdict(float)):
    labels = []
    data = []
    colors = []
    for key, value in expense_dict.items():
        labels.append(key)
        data.append(value)
        colors.append('Red')

    for key, value in income_dict.items():
        labels.append(key)
        data.append(value)
        colors.append('Green')

    return render_template('user/flow.html', title=title, labels=labels, data=data, colors=colors)


@user.route('/flow/details', methods=['GET'])
@login_required
def details_flow():
    income_dict = defaultdict(float)
    expense_dict = defaultdict(float)

    currency, locale, start_date, end_date = get_runtime_settings()
    for entry in current_user.entries:
        entry_date = entry.date
        if entry.type == MoneyEntry.Type.INCOME:
            if (start_date <= entry_date) and (entry_date <= end_date):
                val = exchange_currency(entry.currency, currency, entry.value)
                income_dict[entry.category] += val

        elif entry.type == MoneyEntry.Type.EXPENSE:
            if (start_date <= entry_date) and (entry_date <= end_date):
                val = exchange_currency(entry.currency, currency, entry.value)
                expense_dict[entry.category] += val

    return render_flow(gettext(u'Flow details'), income_dict, expense_dict)
