from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from collections import defaultdict

# ==================== CREATE THE FLASK APP ====================
app = Flask(__name__)
app.secret_key = 'your-super-secret-key-12345'  # Change this in production!

# ==================== FIX: Make 'now' available in templates ====================
@app.context_processor
def inject_now():
    return {'now': datetime.now()}   # ←←← ADD THE () HERE !!!

# ==================== IN-MEMORY STORAGE ====================
categories = {}      # {category_name: limit or None}
transactions = []    # List of transaction dicts


# ==================== HELPER FUNCTION ====================
def calculate_summary():
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    balance = total_income - total_expenses

    spending_by_category = defaultdict(float)
    for t in transactions:
        if t['type'] == 'expense':
            spending_by_category[t['category']] += t['amount']

    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'spending_by_category': dict(spending_by_category)
    }


# ==================== ROUTES ====================

@app.route('/')
def index():
    summary = calculate_summary()
    return render_template('index.html',
                           summary=summary,
                           categories=categories,
                           spending=summary['spending_by_category'])


@app.route('/categories', methods=['GET', 'POST'])
def categories_page():
    if request.method == 'POST':
        name = request.form['name'].strip()
        limit = request.form['limit'].strip()

        if not name:
            flash('Category name is required!', 'danger')
        elif name in categories:
            flash('Category already exists!', 'danger')
        else:
            categories[name] = float(limit) if limit else None
            flash(f'Category "{name}" added!', 'success')
            return redirect(url_for('categories_page'))

    return render_template('categories.html', categories=categories)


@app.route('/transactions', methods=['GET', 'POST'])
def transactions_page():
    if request.method == 'POST':
        try:
            category = request.form['category']
            description = request.form['description']
            amount = float(request.form['amount'])
            trans_type = request.form['type']
            date_str = request.form['datetime']

            # Validation
            if trans_type == 'expense' and category not in categories:
                flash('Please create the category first!', 'danger')
                return redirect(url_for('transactions_page'))

            if amount <= 0:
                flash('Amount must be positive!', 'danger')
                return redirect(url_for('transactions_page'))

            transaction = {
                'category': category if trans_type == 'expense' else 'Income',
                'description': description or '(no description)',
                'amount': amount,
                'type': trans_type,
                'datetime': datetime.strptime(date_str, '%Y-%m-%dT%H:%M'),
                'date_str': date_str
            }
            transactions.append(transaction)
            flash('Transaction added successfully!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash('Invalid input. Please check your data.', 'danger')

    # Display page
    sorted_transactions = sorted(transactions, key=lambda x: x['datetime'], reverse=True)
    return render_template('transactions.html',
                           categories=categories.keys(),
                           transactions=sorted_transactions)


# ==================== RUN THE APP ====================
if __name__ == '__main__':
    app.run(debug=True)