from flask import render_template, redirect, url_for, jsonify, request
from flask_login import logout_user, login_required, current_user

from datetime import datetime
import calendar

from forex_python.converter import CurrencyRates
import app.constants as constants

from app.user import user
from app.home.user_loging_manager import MoneyEntry, Settings, Language
from collections import defaultdict


def new_money_entry(description: str, value: int, currency: str, category: str, date: str):
    dt = datetime.strptime(date, '%m/%d/%Y %H:%M:%S')
    return MoneyEntry(description=description, value=value, currency=currency, category=category, date=dt)


def exchange(fr: str, to: str, amount: float):
    c = CurrencyRates()
    val = c.convert(fr, to, amount)
    return val


def new_money_entry_from_form(form):
    description = form['description']
    value = form['value']
    currency = form['currency']
    category = form['category']
    date = form['date']
    return new_money_entry(description, value, currency, category, date)


def year_month_date(date: datetime):
    dt = date.date()
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    max_dt = datetime(dt.year, dt.month, last_day)
    min_dt = datetime(dt.year, dt.month, 1)
    return min_dt, max_dt


class GraphNode():
    def __init__(self, revenues=0.00, expenses=0.00):
        self.revenues = revenues
        self.expenses = expenses

    expenses = float
    revenues = float


@user.route('/dashboard')
@login_required
def dashboard():
    bar = request.args.to_dict()
    date_range_min, date_range_max = year_month_date(datetime.today())

    revenues = []
    expenses = []
    total = 0.00
    currency = current_user.settings.currency
    language = current_user.settings.language
    graph_dict = defaultdict(GraphNode)
    for rev in current_user.revenues:
        entry_date = rev.date
        entry_date_min, entry_date_max = year_month_date(entry_date)
        if rev.currency == currency:
            rev_val = rev.value
        else:
            rev_val = exchange(rev.currency, currency, rev.value)

        if (date_range_min <= entry_date) and (entry_date <= entry_date_max):
            total += rev_val
            revenues.append(rev)

        graph_dict[entry_date_max].revenues += rev_val

    for exp in current_user.expenses:
        entry_date = exp.date
        entry_date_min, entry_date_max = year_month_date(entry_date)
        if exp.currency == currency:
            exp_val = exp.value
        else:
            exp_val = exchange(exp.currency, currency, exp.value)

        if (date_range_min <= entry_date) and (entry_date <= entry_date_max):
            total -= exp_val
            expenses.append(exp)

        graph_dict[entry_date_max].expenses += exp_val

    chart_labels = []
    chart_revenues = []
    chart_expenses = []
    for key, value in sorted(graph_dict.items()):
        chart_labels.append(key.strftime('%B %Y'))
        chart_revenues.append(value.revenues)
        chart_expenses.append(value.expenses)

    return render_template('user/dashboard.html', total=total, revenues=revenues, expenses=expenses,
                           available_currencies=','.join(constants.AVAILABLE_CURRENCIES),
                           currency=currency, language=language, chart_labels=chart_labels,
                           chart_revenues=chart_revenues, chart_expenses=chart_expenses)


@user.route('/settings')
@login_required
def settings():
    language = current_user.settings.language.to_language()
    currency = current_user.settings.currency
    return render_template('user/settings.html', current_language=language,
                           available_languages=constants.AVAILABLE_LANGUAGES, current_currency=currency,
                           available_currencies=','.join(constants.AVAILABLE_CURRENCIES))


@user.route('/settings/apply', methods=['POST'])
@login_required
def settings_apply():
    currency = request.form['currency']
    language = request.form['language']
    lang = constants.get_language_by_name(language)
    dblang = Language(lang.language(), lang.locale())
    current_user.settings = Settings(currency=currency, language=dblang)
    current_user.save()
    response = {}
    return jsonify(response), 200


@user.route('/logout')
@login_required
def logout():
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

    return render_template('user/details.html', title=title, labels=labels, data=data,
                           colors=constants.AVAILIBLE_CHART_COLORS)


# revenue
@user.route('/revenue/details', methods=['GET'])
@login_required
def details_revenue():
    currency = current_user.settings.currency
    return render_details('Revenue details', currency, current_user.revenues)


@user.route('/revenue/add', methods=['POST'])
@login_required
def add_revenue():
    new_revenue = new_money_entry_from_form(request.form)
    inserted = False
    for index, value in enumerate(current_user.revenues):
        if value.date > new_revenue.date:
            current_user.revenues.insert(index, new_revenue)
            inserted = True
            break

    if not inserted:
        current_user.revenues.append(new_revenue)

    current_user.save()

    response = {"revenue_id": str(new_revenue.id)}
    return jsonify(response), 200


@user.route('/revenue/remove', methods=['POST'])
@login_required
def remove_revenue():
    revenue_id = request.form['revenue_id']

    for revenue in current_user.revenues:
        if str(revenue.id) == revenue_id:
            current_user.revenues.remove(revenue)
            current_user.save()
            break

    response = {"revenue_id": revenue_id}
    return jsonify(response), 200


@user.route('/revenue/add_category', methods=['POST'])
@login_required
def add_category_revenue():
    category = request.form['category']
    current_user.revenues_categories.append(category)
    current_user.save()

    response = {}
    return jsonify(response), 200


@user.route('/revenue/remove_category', methods=['POST'])
@login_required
def remove_category_revenue():
    category = request.form['category']
    current_user.revenues_categories.remove(category)
    current_user.save()

    response = {}
    return jsonify(response), 200


# expense
@user.route('/expense/details', methods=['GET'])
@login_required
def details_expense():
    currency = current_user.settings.currency
    return render_details('Expense details', currency, current_user.expenses)


@user.route('/expense/add', methods=['POST'])
@login_required
def add_expense():
    new_expense = new_money_entry_from_form(request.form)
    inserted = False
    for index, value in enumerate(current_user.expenses):
        if value.date > new_expense.date:
            current_user.expenses.insert(index, new_expense)
            inserted = True
            break

    if not inserted:
        current_user.expenses.append(new_expense)

    current_user.save()

    response = {"expense_id": str(new_expense.id)}
    return jsonify(response), 200


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
