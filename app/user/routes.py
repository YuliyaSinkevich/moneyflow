from flask import render_template, redirect, url_for, jsonify, request
from flask_login import logout_user, login_required, current_user

from datetime import datetime
from forex_python.converter import CurrencyRates

from app.user import user
from app.home.user_loging_manager import MoneyEntry

AVAILABLE_CURRENCIES = ['EUR', 'AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK', 'GBP', 'HKD', 'HRK', 'HUF',
                        'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'MXN', 'MYR', 'NOK', 'NZD', 'PHP', 'PLN', 'RON',
                        'RUB', 'SEK', 'SGD', 'THB', 'TRY', 'USD', 'ZAR']


def new_money_entry(description: str, value: int, currency: str, category: str, date: str):
    dt = datetime.strptime(date, '%m/%d/%Y %I:%M %p')
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


@user.route('/dashboard')
@login_required
def dashboard():
    total = 0.00
    currency = 'USD'
    language = 'en'
    for rev in current_user.revenues:
        if rev.currency == currency:
            total += rev.value
        else:
            total += exchange(rev.currency, currency, rev.value)

    for exp in current_user.expenses:
        if exp.currency == currency:
            total -= exp.value
        else:
            total -= exchange(exp.currency, currency, exp.value)

    return render_template('user/dashboard.html', total=total, available_currencies=','.join(AVAILABLE_CURRENCIES),
                           currency=currency, language=language)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.start'))


@user.route('/revenue/add', methods=['POST'])
@login_required
def add_revenue():
    new_revenue = new_money_entry_from_form(request.form)
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


@user.route('/expense/add', methods=['POST'])
@login_required
def add_expense():
    new_expense = new_money_entry_from_form(request.form)
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
