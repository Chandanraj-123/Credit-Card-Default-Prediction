from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from config import Config
from models import db, CustomerAccountDetails, ManagerDetails, YearlySummary, CustomerYearPercentage, yearly_models
from ml_model import train_model, predict_credit_score
import pymysql

# Ensure pymysql is used as MySQLdb
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db.init_app(app)

# Helper to get yearly model
def get_yearly_model(year, type='pay'):
    # type: 'pay' or 'paid'
    key = f'CustomerAmount{"ToBePay" if type == "pay" else "Paid"}{year}'
    return yearly_models.get(key)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manager-login')
def manager_login():
    return render_template('manager_login.html')

@app.route('/customer-login')
def customer_login():
    return render_template('customer_login.html')

# API Routes
@app.route('/api/manager/login', methods=['POST'])
def manager_login_api():
    data = request.json
    manager = ManagerDetails.query.filter_by(id=data['id'], password=data['password']).first()
    
    if manager:
        session['manager_id'] = manager.id
        return jsonify({
            'success': True, 
            'data': {
                'id': manager.id,
                'name': manager.name,
                'mailid': manager.mailid,
                'phone_number': manager.phone_number
            }
        })
    return jsonify({'success': False, 'message': 'Incorrect data please check id and password'})

@app.route('/api/customer/login', methods=['POST'])
def customer_login_api():
    data = request.json
    customer = CustomerAccountDetails.query.filter_by(id=data['id'], password=data['password']).first()
    
    if customer:
        session['customer_id'] = customer.id
        return jsonify({
            'success': True, 
            'data': {
                'id': customer.id,
                'name': customer.name,
                'mailid': customer.mailid,
                'phone_number': customer.phone_number
            }
        })
    return jsonify({'success': False, 'message': 'Incorrect data please check id and password'})

@app.route('/api/customer/summary/<int:customer_id>')
def customer_summary(customer_id):
    total_credit = 0
    total_paid = 0
    
    for year in [2021, 2022, 2023, 2024, 2025]:
        PayModel = get_yearly_model(year, 'pay')
        PaidModel = get_yearly_model(year, 'paid')
        
        to_pay = PayModel.query.get(customer_id)
        paid = PaidModel.query.get(customer_id)
        
        if to_pay:
            total_credit += float(to_pay.total_amount_to_be_pay or 0)
        if paid:
            total_paid += float(paid.total_paid_amt or 0)
    
    balance = total_credit - total_paid
    
    return jsonify({
        'total_credit': total_credit,
        'total_paid': total_paid,
        'balance': balance
    })

@app.route('/api/customer/data/<int:customer_id>/<year>')
def customer_data_by_year(customer_id, year):
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    
    if year == 'all':
        all_data = []
        for y in [2021, 2022, 2023, 2024, 2025]:
            PayModel = get_yearly_model(y, 'pay')
            PaidModel = get_yearly_model(y, 'paid')
            
            to_pay = PayModel.query.get(customer_id)
            paid = PaidModel.query.get(customer_id)
            
            if to_pay and paid:
                for month in months:
                    amt_given = getattr(to_pay, f'{month}_amt') or 0
                    amt_paid = getattr(paid, f'{month}_amt') or 0
                    all_data.append({
                        'year': y,
                        'month': month.capitalize(),
                        'amount_given': float(amt_given),
                        'paid': float(amt_paid),
                        'balance': float(amt_given - amt_paid)
                    })
        return jsonify(all_data)
    else:
        y = int(year)
        PayModel = get_yearly_model(y, 'pay')
        PaidModel = get_yearly_model(y, 'paid')
        
        to_pay = PayModel.query.get(customer_id)
        paid = PaidModel.query.get(customer_id)
        
        data = []
        if to_pay and paid:
            for month in months:
                amt_given = getattr(to_pay, f'{month}_amt') or 0
                amt_paid = getattr(paid, f'{month}_amt') or 0
                data.append({
                    'month': month.capitalize(),
                    'amount_given': float(amt_given),
                    'paid': float(amt_paid),
                    'balance': float(amt_given - amt_paid)
                })
        
        return jsonify(data)

@app.route('/api/customer/payment', methods=['POST'])
def process_payment():
    data = request.json
    customer_id = data['customer_id']
    year = int(data['year'])
    month = data['month'].lower()[:3]
    amount = float(data['amount'])
    
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    remaining_amount = amount
    payments_made = []
    
    # Start from the specified year and month
    years = [y for y in [2021, 2022, 2023, 2024, 2025] if y >= year]
    start_month_idx = months.index(month) if year == years[0] else 0
    
    try:
        for y in years:
            PayModel = get_yearly_model(y, 'pay')
            PaidModel = get_yearly_model(y, 'paid')
            
            to_pay_row = PayModel.query.get(customer_id)
            paid_row = PaidModel.query.get(customer_id)
            
            if not to_pay_row or not paid_row:
                continue
            
            month_start = start_month_idx if y == years[0] else 0
            
            for i in range(month_start, len(months)):
                m = months[i]
                due = float(getattr(to_pay_row, f'{m}_amt') or 0) - float(getattr(paid_row, f'{m}_amt') or 0)
                
                if due > 0 and remaining_amount > 0:
                    payment = min(due, remaining_amount)
                    current_paid = float(getattr(paid_row, f'{m}_amt') or 0)
                    setattr(paid_row, f'{m}_amt', current_paid + payment)
                    
                    remaining_amount -= payment
                    payments_made.append({'year': y, 'month': m, 'amount': payment})
            
            # Update totals for the year
            total_paid_year = sum([float(getattr(paid_row, f'{m}_amt') or 0) for m in months])
            paid_row.total_paid_amt = total_paid_year
            
            # Update yearly summary table if needed (optional based on requirements)
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'payments_made': payments_made,
            'excess_amount': remaining_amount,
            'message': 'All amount is paid. The exceeded amount will be credited to bank account' if remaining_amount > 0 else 'Payment successful'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/customer/credit-request', methods=['POST'])
def credit_request():
    data = request.json
    method = data['method']
    customer_id = data['customer_id']
    
    if method == 'percentage':
        total_to_pay = 0
        total_paid = 0
        
        for year in [2021, 2022, 2023, 2024, 2025]:
            PayModel = get_yearly_model(year, 'pay')
            PaidModel = get_yearly_model(year, 'paid')
            
            to_pay = PayModel.query.get(customer_id)
            paid = PaidModel.query.get(customer_id)
            
            if to_pay:
                total_to_pay += float(to_pay.total_amount_to_be_pay or 0)
            if paid:
                total_paid += float(paid.total_paid_amt or 0)
        
        percentage_paid = (total_paid / total_to_pay * 100) if total_to_pay > 0 else 0
        approved = percentage_paid >= 80
        
        if approved:
            # Add credit to the specified month/year
            year = int(data['year'])
            month = data['month'].lower()[:3]
            amount = float(data['amount'])
            
            PayModel = get_yearly_model(year, 'pay')
            to_pay_row = PayModel.query.get(customer_id)
            
            if to_pay_row:
                current_amt = float(getattr(to_pay_row, f'{month}_amt') or 0)
                setattr(to_pay_row, f'{month}_amt', current_amt + amount)
                
                # Update total
                months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                total_amt_year = sum([float(getattr(to_pay_row, f'{m}_amt') or 0) for m in months])
                to_pay_row.total_amount_to_be_pay = total_amt_year
                
                db.session.commit()
        
        return jsonify({
            'approved': approved,
            'percentage_paid': percentage_paid,
            'total_paid': total_paid,
            'balance': total_to_pay - total_paid
        })
    
    elif method == 'ml':
        percentages = CustomerYearPercentage.query.get(customer_id)
        
        if not percentages:
            return jsonify({'approved': False, 'message': 'No data found'})
        
        features = [
            float(percentages.year_2021 or 0),
            float(percentages.year_2022 or 0),
            float(percentages.year_2023 or 0),
            float(percentages.year_2024 or 0),
            float(percentages.year_2025 or 0)
        ]
        
        prediction = predict_credit_score(features)
        approved = bool(prediction)
        
        if approved:
            # Add credit
            year = int(data['year'])
            month = data['month'].lower()[:3]
            amount = float(data['amount'])
            
            PayModel = get_yearly_model(year, 'pay')
            to_pay_row = PayModel.query.get(customer_id)
            
            if to_pay_row:
                current_amt = float(getattr(to_pay_row, f'{month}_amt') or 0)
                setattr(to_pay_row, f'{month}_amt', current_amt + amount)
                
                # Update total
                months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                total_amt_year = sum([float(getattr(to_pay_row, f'{m}_amt') or 0) for m in months])
                to_pay_row.total_amount_to_be_pay = total_amt_year
                
                db.session.commit()
        
        return jsonify({
            'approved': approved,
            'percentages': {
                'year_2021': float(percentages.year_2021 or 0),
                'year_2022': float(percentages.year_2022 or 0),
                'year_2023': float(percentages.year_2023 or 0),
                'year_2024': float(percentages.year_2024 or 0),
                'year_2025': float(percentages.year_2025 or 0)
            },
            'score': sum(features)/len(features) # Return avg as score for display
        })

@app.route('/api/ml/train', methods=['POST'])
def train_ml_model():
    # Fetch all data from CustomerYearPercentage
    all_data = CustomerYearPercentage.query.all()
    training_data = []
    
    for row in all_data:
        training_data.append({
            'year_2021': float(row.year_2021 or 0),
            'year_2022': float(row.year_2022 or 0),
            'year_2023': float(row.year_2023 or 0),
            'year_2024': float(row.year_2024 or 0),
            'year_2025': float(row.year_2025 or 0),
            'result': float(row.result or 0)
        })
    
    if not training_data:
        return jsonify({'success': False, 'message': 'No training data available'})
        
    accuracy = train_model(training_data)
    
    return jsonify({
        'success': True,
        'accuracy': accuracy,
        'message': f'Model trained successfully with accuracy: {accuracy}'
    })

@app.route('/api/customer/calculate-percentages', methods=['POST'])
def calculate_percentages():
    data = request.json
    customer_id = data['customer_id']
    
    total_given_all = 0
    total_paid_all = 0
    yearly_percentages = {}
    
    try:
        # Calculate for each year
        for year in [2021, 2022, 2023, 2024, 2025]:
            PayModel = get_yearly_model(year, 'pay')
            PaidModel = get_yearly_model(year, 'paid')
            
            to_pay = PayModel.query.get(customer_id)
            paid = PaidModel.query.get(customer_id)
            
            amt_given = float(to_pay.total_amount_to_be_pay or 0) if to_pay else 0
            amt_paid = float(paid.total_paid_amt or 0) if paid else 0
            
            total_given_all += amt_given
            total_paid_all += amt_paid
            
            percentage = (amt_paid / amt_given) if amt_given > 0 else 0
            yearly_percentages[f'year_{year}'] = percentage
            
        # Update CustomerYearPercentage table
        percentages_row = CustomerYearPercentage.query.get(customer_id)
        if not percentages_row:
            percentages_row = CustomerYearPercentage(id=customer_id)
            db.session.add(percentages_row)
        
        percentages_row.year_2021 = yearly_percentages['year_2021']
        percentages_row.year_2022 = yearly_percentages['year_2022']
        percentages_row.year_2023 = yearly_percentages['year_2023']
        percentages_row.year_2024 = yearly_percentages['year_2024']
        percentages_row.year_2025 = yearly_percentages['year_2025']
        
        # Calculate result (average or total percentage)
        # User said: "Percentage Paid=(T/P)*100" (Wait, T/P? Usually P/T. User said T/P but formula usually P/T. 
        # "Total Loan Amount (T)... Amount Paid (P)... Percentage Paid=(T/P)*100" -> If T=1000, P=500, T/P = 2 * 100 = 200%. That's wrong.
        # It should be P/T. "Amount Paid so far (P) ... Percentage Paid=(P/T)*100".
        # User wrote: "Percentage Paid=(T/P​)×100". I will assume they meant P/T because otherwise it doesn't make sense for credit eligibility (higher is better).
        # "Total Amount paid Percentage Should be more than 80%." -> This implies P/T.
        
        total_percentage = (total_paid_all / total_given_all * 100) if total_given_all > 0 else 0
        percentages_row.result = total_percentage / 100 # Store as 0.0-1.0 or 0-100? User said "0.0 to 1.0" for years.
        # "result DECIMAL(5,2)" in table.
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'percentages': yearly_percentages,
            'total_given': total_given_all,
            'total_paid': total_paid_all,
            'total_percentage': total_percentage
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/manager-home')
def manager_home():
    return render_template('manager_home.html')

@app.route('/customer-home')
def customer_home():
    return render_template('customer_home.html')

@app.route('/customer-payment')
def customer_payment():
    return render_template('customer_payment.html')

@app.route('/credit-request')
def credit_request_page():
    return render_template('credit_request.html')

@app.route('/credit-sanctioned')
def credit_sanctioned():
    return render_template('credit_sanctioned.html')

@app.route('/credit-rejected')
def credit_rejected():
    return render_template('credit_rejected.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)