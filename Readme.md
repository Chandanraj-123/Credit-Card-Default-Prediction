\# Credit Management System - Flask REST API Application



A comprehensive credit management system built with Flask, featuring customer and manager portals, payment processing, and ML-based credit approval.



\## Features



\### Manager Portal

\- Secure login with ID and password

\- Dashboard displaying manager details

\- Eye icon for password visibility toggle



\### Customer Portal

\- Secure login with ID and password

\- Comprehensive dashboard with:

&nbsp; - Customer details display

&nbsp; - Total credit, paid amount, and balance summary

&nbsp; - Year-wise payment filtering (2021-2025)

&nbsp; - Detailed monthly payment breakdown

&nbsp; - Horizontal and vertical scrolling for large tables



\### Payment Processing

\- Make payments for specific month/year

\- Automatic distribution of excess payments

\- Real-time balance updates

\- Payment history tracking



\### Credit Request System

Two methods for credit approval:



1\. \*\*Percentage-Based Method\*\*

&nbsp;  - Calculates total paid percentage

&nbsp;  - Approves if >= 80% paid

&nbsp;  - Automatic credit addition to account



2\. \*\*ML Model Method\*\*

&nbsp;  - Displays yearly payment percentages

&nbsp;  - Uses ML prediction for approval

&nbsp;  - Score-based decision making



\## Project Structure



```

credit\_management\_system/

│

├── app.py                      # Main Flask application

├── credit\_management.db        # SQLite database (auto-generated)

├── requirements.txt            # Python dependencies

│

└── templates/

&nbsp;   ├── index.html              # Main landing page

&nbsp;   ├── manager\_login.html      # Manager login page

&nbsp;   ├── manager\_home.html       # Manager dashboard

&nbsp;   ├── customer\_login.html     # Customer login page

&nbsp;   ├── customer\_home.html      # Customer dashboard

&nbsp;   ├── customer\_payment.html   # Payment processing page

&nbsp;   ├── credit\_request.html     # Credit request page

&nbsp;   ├── credit\_sanctioned.html  # Approval confirmation page

&nbsp;   └── credit\_rejected.html    # Rejection notification page

```



\## Database Schema



\### 1. customer\_account\_details

\- id (INTEGER, PRIMARY KEY)

\- password (TEXT)

\- name (TEXT)

\- mailid (TEXT)

\- age (INTEGER)

\- phone (TEXT)



\### 2. amount\_to\_pay\_{year} (2021-2025)

\- id (INTEGER, PRIMARY KEY)

\- jan\_amt through dec\_amt (REAL)

\- total\_amt (REAL)



\### 3. amount\_paid\_{year} (2021-2025)

\- id (INTEGER, PRIMARY KEY)

\- jan\_amt through dec\_amt (REAL)

\- total\_paid\_amt (REAL)

\- needtopay (REAL)



\### 4. year\_percentage

\- id (INTEGER, PRIMARY KEY)

\- y2021 through y2025 (REAL)

\- result (INTEGER)



\### 5. manager\_details

\- id (INTEGER, PRIMARY KEY)

\- password (TEXT)

\- name (TEXT)

\- mailid (TEXT)

\- age (INTEGER)

\- phone (TEXT)



\## Setup Instructions



\### Prerequisites

\- Python 3.8 or higher

\- pip (Python package manager)



\### Installation Steps



1\. \*\*Create project directory:\*\*

```bash

mkdir credit\_management\_system

cd credit\_management\_system

```



2\. \*\*Create requirements.txt:\*\*

```txt

Flask==3.0.0

flask-cors==4.0.0

numpy==1.24.3

scikit-learn==1.3.0

```



3\. \*\*Install dependencies:\*\*

```bash

pip install -r requirements.txt

```



4\. \*\*Create templates directory:\*\*

```bash

mkdir templates

```



5\. \*\*Add all HTML files to templates directory\*\* (provided separately)



6\. \*\*Run the application:\*\*

```bash

python app.py

```



7\. \*\*Access the application:\*\*

Open your browser and navigate to:

```

http://127.0.0.1:5000/

```



\## Default Login Credentials



\### Manager

\- \*\*ID:\*\* 1

\- \*\*Password:\*\* manager123



\### Customer

\- \*\*ID:\*\* 101

\- \*\*Password:\*\* customer123



\## API Endpoints



\### Authentication

\- `POST /api/manager/login` - Manager login

\- `POST /api/customer/login` - Customer login



\### Customer Operations

\- `GET /api/customer/summary/<customer\_id>` - Get financial summary

\- `GET /api/customer/data/<customer\_id>/<year>` - Get year-specific data

\- `POST /api/customer/payment` - Process payment

\- `POST /api/customer/credit-request` - Request credit



\## Usage Guide



\### For Customers



1\. \*\*Login:\*\*

&nbsp;  - Navigate to main page

&nbsp;  - Click "Customer" button

&nbsp;  - Enter ID and password

&nbsp;  - Toggle password visibility with eye icon



2\. \*\*View Dashboard:\*\*

&nbsp;  - See personal details

&nbsp;  - View total credit, paid amount, and balance

&nbsp;  - Use year filter to view specific year data

&nbsp;  - Click "Apply Filter" to refresh table



3\. \*\*Make Payment:\*\*

&nbsp;  - Click "Pay" button

&nbsp;  - Select year and month

&nbsp;  - Enter payment amount

&nbsp;  - Submit to process payment

&nbsp;  - View payment distribution



4\. \*\*Request Credit:\*\*

&nbsp;  - Click "Credit Request" button

&nbsp;  - Enter year, month, and amount

&nbsp;  - Choose approval method:

&nbsp;    - \*\*Total Amount Paid:\*\* Instant percentage calculation

&nbsp;    - \*\*ML Model:\*\* View percentages and get prediction

&nbsp;  - Wait for credit score checking

&nbsp;  - View approval or rejection



\### For Managers



1\. \*\*Login:\*\*

&nbsp;  - Navigate to main page

&nbsp;  - Click "Manager" button

&nbsp;  - Enter credentials

&nbsp;  - View dashboard with manager details



\## Key Features Explained



\### Payment Distribution Logic

\- Payments are applied starting from the specified month

\- Excess payments automatically flow to subsequent months

\- If all dues are cleared, excess amount is noted for bank credit

\- Real-time balance updates across all years



\### Credit Approval Logic



\*\*Percentage Method:\*\*

\- Calculates: (Total Paid / Total Due) × 100

\- Approves if percentage >= 80%



\*\*ML Model Method:\*\*

\- Analyzes 5-year payment history

\- Considers payment consistency

\- Uses average percentage for prediction

\- Requires score >= 0.8 for approval



\### Security Features

\- Password hashing support ready

\- Session management

\- Input validation

\- SQL injection prevention through parameterized queries



\## Customization



\### Adding New Users



\*\*Manager:\*\*

```python

cursor.execute("INSERT INTO manager\_details VALUES (?, ?, ?, ?, ?, ?)", 

&nbsp;             (id, password, name, email, age, phone))

```



\*\*Customer:\*\*

```python

cursor.execute("INSERT INTO customer\_account\_details VALUES (?, ?, ?, ?, ?, ?)", 

&nbsp;             (id, password, name, email, age, phone))

```



\### Modifying Credit Approval Threshold

In `app.py`, change the approval condition:

```python

approved = percentage\_paid >= 80  # Change 80 to your desired percentage

```



\## Troubleshooting



\### Database Issues

If database gets corrupted:

```bash

rm credit\_management.db

python app.py  # Will recreate database

```



\### Port Already in Use

Change port in `app.py`:

```python

app.run(debug=True, port=5001)

```



\### Import Errors

Ensure all dependencies are installed:

```bash

pip install -r requirements.txt --upgrade

```



\## Future Enhancements



\- \[ ] Add password encryption

\- \[ ] Implement JWT authentication

\- \[ ] Add email notifications

\- \[ ] Export payment history to PDF

\- \[ ] Advanced ML model training interface

\- \[ ] Multi-language support

\- \[ ] Mobile responsive improvements

\- \[ ] Admin panel for user management



\## License

This project is open source and available for educational purposes.



\## Support

For issues or questions, please create an issue in the project repository.

