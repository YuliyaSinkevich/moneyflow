from flask import render_template, redirect, url_for, jsonify, request
from flask_login import logout_user, login_required, current_user

from app.user import user
from app.home.user_loging_manager import MoneyEntry


def new_money_entry(description: str, value: int, currency: str, category: str, date: str):
    return MoneyEntry(description=description, value=value, currency=currency, category=category)


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
    for rev in current_user.revenues:
        total += rev.value

    for exp in current_user.expenses:
        total -= exp.value

    return render_template('user/dashboard.html', total=total, currency='USD', language='en')


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
