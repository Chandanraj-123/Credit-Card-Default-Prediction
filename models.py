from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class CustomerAccountDetails(db.Model):
    __tablename__ = 'customer_account_details'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    mailid = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer)
    phone_number = db.Column(db.String(20))

class ManagerDetails(db.Model):
    __tablename__ = 'manager_details'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    mailid = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer)
    phone_number = db.Column(db.String(20))

class YearlySummary(db.Model):
    __tablename__ = 'yearly_summary'
    year = db.Column(db.Integer, primary_key=True)
    total_amount_given = db.Column(db.Numeric(15, 2))
    total_amount_paid = db.Column(db.Numeric(15, 2))
    percentage_paid = db.Column(db.Numeric(6, 2))

class CustomerYearPercentage(db.Model):
    __tablename__ = 'customer_year_percentage'
    id = db.Column(db.Integer, primary_key=True)
    year_2021 = db.Column(db.Numeric(5, 2))
    year_2022 = db.Column(db.Numeric(5, 2))
    year_2023 = db.Column(db.Numeric(5, 2))
    year_2024 = db.Column(db.Numeric(5, 2))
    year_2025 = db.Column(db.Numeric(5, 2))
    result = db.Column(db.Numeric(5, 2))

# Dynamic model creation for yearly tables to avoid repetition
def create_yearly_models():
    models = {}
    years = [2021, 2022, 2023, 2024, 2025]
    
    for year in years:
        # Amount To Be Pay Table
        class_name_pay = f'CustomerAmountToBePay{year}'
        table_name_pay = f'customer_amount_to_be_pay_{year}'
        
        attributes_pay = {
            '__tablename__': table_name_pay,
            'id': db.Column(db.Integer, primary_key=True),
            'jan_amt': db.Column(db.Numeric(10, 2)),
            'feb_amt': db.Column(db.Numeric(10, 2)),
            'mar_amt': db.Column(db.Numeric(10, 2)),
            'apr_amt': db.Column(db.Numeric(10, 2)),
            'may_amt': db.Column(db.Numeric(10, 2)),
            'jun_amt': db.Column(db.Numeric(10, 2)),
            'jul_amt': db.Column(db.Numeric(10, 2)),
            'aug_amt': db.Column(db.Numeric(10, 2)),
            'sep_amt': db.Column(db.Numeric(10, 2)),
            'oct_amt': db.Column(db.Numeric(10, 2)),
            'nov_amt': db.Column(db.Numeric(10, 2)),
            'dec_amt': db.Column(db.Numeric(10, 2)),
            'total_amount_to_be_pay': db.Column(db.Numeric(10, 2))
        }
        
        models[class_name_pay] = type(class_name_pay, (db.Model,), attributes_pay)
        
        # Amount Paid Table
        class_name_paid = f'CustomerAmountPaid{year}'
        table_name_paid = f'customer_amount_paid_{year}'
        
        attributes_paid = {
            '__tablename__': table_name_paid,
            'id': db.Column(db.Integer, primary_key=True),
            'jan_amt': db.Column(db.Numeric(10, 2)),
            'feb_amt': db.Column(db.Numeric(10, 2)),
            'mar_amt': db.Column(db.Numeric(10, 2)),
            'apr_amt': db.Column(db.Numeric(10, 2)),
            'may_amt': db.Column(db.Numeric(10, 2)),
            'jun_amt': db.Column(db.Numeric(10, 2)),
            'jul_amt': db.Column(db.Numeric(10, 2)),
            'aug_amt': db.Column(db.Numeric(10, 2)),
            'sep_amt': db.Column(db.Numeric(10, 2)),
            'oct_amt': db.Column(db.Numeric(10, 2)),
            'nov_amt': db.Column(db.Numeric(10, 2)),
            'dec_amt': db.Column(db.Numeric(10, 2)),
            'total_paid_amt': db.Column(db.Numeric(10, 2))
        }
        
        models[class_name_paid] = type(class_name_paid, (db.Model,), attributes_paid)
        
    return models

yearly_models = create_yearly_models()
