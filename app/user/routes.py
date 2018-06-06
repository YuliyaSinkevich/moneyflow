from flask import render_template, redirect, url_for, jsonify, request, session
from flask_login import logout_user, login_required, current_user

from datetime import datetime
from random import shuffle

import app.constants as constants
import app.utils as utils
from .forms import MoneyEntryForm
from app import exchange_client

from app.user import user
from app.home.user_loging_manager import MoneyEntry, Settings, Language, DateRange
from collections import defaultdict

AVAILABLE_CURRENCIES_FOR_COMBO = ','.join(constants.AVAILABLE_CURRENCIES)
DATE_JS_FORMAT = '%m/%d/%Y %H:%M:%S'


def new_money_entry(description: str, value: float, currency: str, category: str, date: datetime) -> MoneyEntry:
    return MoneyEntry(description=description, value=value, currency=currency, category=category, date=date)


def exchange(base: str, to: str, amount: float) -> float:
    json = exchange_client.get_rates(base)
    if not json:
        return 0.00

    rates = json[to]
    return amount * rates


def new_money_entry_from_form(form: MoneyEntryForm) -> MoneyEntry:
    description = form.description.data
    value = form.value.data
    currency = form.currency.data
    category_pos = form.category.data
    categories = form.category.choices
    category = categories[category_pos]
    date = form.date.data
    return new_money_entry(description, value, currency, category[1], date)


def update_money_entry_from_form(entry: MoneyEntry, form: MoneyEntryForm) -> MoneyEntry:
    entry.description = form.description.data
    entry.value = form.value.data
    entry.currency = form.currency.data
    category_pos = form.category.data
    categories = form.category.choices
    entry.category = categories[category_pos][1]
    entry.date = form.date.data


class GraphNode(object):
    def __init__(self, incomes=0.00, expenses=0.00):
        self.incomes = incomes
        self.expenses = expenses

    expenses = float
    incomes = float


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
    start_date = rsettings.date_range.start_date
    end_date = rsettings.date_range.end_date

    for rev in current_user.incomes:
        entry_date = rev.date
        entry_date_min, entry_date_max = utils.year_month_date(entry_date)
        if rev.currency == currency:
            rev_val = rev.value
        else:
            rev_val = exchange(rev.currency, currency, rev.value)

        if (start_date <= entry_date) and (entry_date <= end_date):
            total += rev_val
            incomes.append(rev)

        graph_dict[entry_date_max].incomes += rev_val

    for exp in current_user.expenses:
        entry_date = exp.date
        entry_date_min, entry_date_max = utils.year_month_date(entry_date)
        if exp.currency == currency:
            exp_val = exp.value
        else:
            exp_val = exchange(exp.currency, currency, exp.value)

        if (start_date <= entry_date) and (entry_date <= end_date):
            total -= exp_val
            expenses.append(exp)

        graph_dict[entry_date_max].expenses += exp_val

    chart_labels = []
    chart_incomes = []
    chart_expenses = []
    for key, value in sorted(graph_dict.items()):
        chart_labels.append(key.strftime('%B %Y'))
        chart_incomes.append(value.incomes)
        chart_expenses.append(value.expenses)

    entry_date_str = datetime.today().now().strftime(DATE_JS_FORMAT)
    return render_template('user/dashboard.html', total=total, incomes=incomes, expenses=expenses,
                           currency=currency, available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO,
                           language=language, chart_labels=chart_labels,
                           chart_incomes=chart_incomes, chart_expenses=chart_expenses, entry_date=entry_date_str)


@user.route('/settings')
@login_required
def settings():
    rsettings = current_user.settings
    language = rsettings.language.to_language()
    currency = rsettings.currency
    start_date_str = rsettings.date_range.start_date.strftime(DATE_JS_FORMAT)
    end_date_str = rsettings.date_range.end_date.strftime(DATE_JS_FORMAT)
    return render_template('user/settings.html', current_language=language,
                           available_languages=constants.AVAILABLE_LANGUAGES, current_currency=currency,
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
    date_range = DateRange(datetime.strptime(start_date, DATE_JS_FORMAT),
                           datetime.strptime(end_date, DATE_JS_FORMAT))
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
        r = round(value / total, 2)
        data.append(r)

    colors = list(constants.AVAILIBLE_CHART_COLORS)
    shuffle(colors)
    return render_template('user/details.html', title=title, labels=labels, data=data,
                           colors=colors[:len(data)])


# income
@user.route('/income/details', methods=['GET'])
@login_required
def details_income():
    currency = current_user.settings.currency
    return render_details('Income details', currency, current_user.incomes)


def add_money_entry(categories: list, language: Language, save_callback):
    extended_cat = []
    for index, value in enumerate(categories):
        extended_cat.append((index, value))

    form = MoneyEntryForm()
    form.category.choices = extended_cat

    if form.validate_on_submit():
        new_entry = new_money_entry_from_form(form)
        save_callback(new_entry)
        return jsonify(status='ok'), 200

    return render_template('user/money/add.html', form=form, language=language,
                           available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO)


def edit_money_entry(method: str, entry: MoneyEntry, categories: list, language: Language):
    extended_cat = []
    category_index = 0
    for index, value in enumerate(categories):
        if entry.category == value:
            category_index = index
        extended_cat.append((index, value))

    form = MoneyEntryForm()
    form.category.choices = extended_cat

    if method == 'GET':
        # init form
        form.date.data = entry.date
        form.category.data = category_index
        form.value.data = entry.value
        form.currency.data = entry.currency
        form.description.data = entry.description

    if method == 'POST' and form.validate_on_submit():
        update_money_entry_from_form(entry, form)
        entry.save()
        return jsonify(status='ok'), 200

    return render_template('user/money/edit.html', form=form, language=language,
                           available_currencies=AVAILABLE_CURRENCIES_FOR_COMBO)


@user.route('/income/add', methods=['GET', 'POST'])
@login_required
def add_income():
    def insert_income(new_entry: MoneyEntry):
        current_user.incomes.append(new_entry)
        current_user.save()

    rsettings = current_user.settings
    language = rsettings.language
    return add_money_entry(current_user.incomes_categories, language, insert_income)


@user.route('/income/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_income(id):
    for income in current_user.incomes:
        if str(income.id) == id:
            rsettings = current_user.settings
            language = rsettings.language
            return edit_money_entry(request.method, income, current_user.incomes_categories, language)

    responce = {"status": "failed"}
    return jsonify(responce), 404


@user.route('/income/remove', methods=['POST'])
@login_required
def remove_income():
    income_id = request.form['income_id']

    for income in current_user.incomes:
        if str(income.id) == income_id:
            current_user.incomes.remove(income)
            current_user.save()
            break

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
    def insert_expense(new_entry: MoneyEntry):
        current_user.expenses.append(new_entry)
        current_user.save()

    rsettings = current_user.settings
    language = rsettings.language
    return add_money_entry(current_user.expenses_categories, language, insert_expense)


@user.route('/expense/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    for expense in current_user.expenses:
        if str(expense.id) == id:
            rsettings = current_user.settings
            language = rsettings.language
            return edit_money_entry(request.method, expense, current_user.expenses_categories, language)

    responce = {"status": "failed"}
    return jsonify(responce), 404


@user.route('/expense/remove', methods=['POST'])
@login_required
def remove_expense():
    expense_id = request.form['expense_id']

    for expense in current_user.expenses:
        if str(expense.id) == expense_id:
            current_user.expenses.remove(expense)
            current_user.save()
            break

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
