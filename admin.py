import logging, csv, io, psycopg2, uuid
from flask import flash, request, jsonify, render_template, redirect, url_for, session, Blueprint
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from db import get_db_connection
from threading import Lock

import_lock = Lock()
admin_bp = Blueprint('admin', __name__)
ALLOWED_EXTENSIONS = {'csv'}

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("CREATE INDEX idx_account_customerid ON account (customerid);")
cursor.execute("CREATE INDEX idx_account_dateopened ON account (dateopened);")
cursor.execute("CREATE INDEX idx_account_balance ON account (balance);")
cursor.close()
conn.close()

@admin_bp.route('/view_all_customers', methods=['GET'])
def view_all_data():
    # Base SQL query with CTEs
    AGGREGATE_QUERY = """
    WITH AccountSummary AS (
        SELECT 
            customerid, 
            COUNT(accountid) AS account_count, 
            COALESCE(SUM(balance), 0) AS total_balance, 
            MIN(dateopened) AS first_account_opened, 
            MAX(dateopened) AS latest_account_opened
        FROM account
        GROUP BY customerid
    ),
    LoanSummary AS (
        SELECT 
            customerid, 
            COUNT(loanid) AS loan_count, 
            COALESCE(SUM(principalamount), 0) AS total_loan_amount
        FROM loan
        GROUP BY customerid
    ),
    PaymentSummary AS (
        SELECT 
            l.customerid, 
            COUNT(lp.paymentid) AS payment_count, 
            COALESCE(SUM(lp.amount), 0) AS total_payment_amount
        FROM loanpayment lp
        JOIN loan l ON lp.loanid = l.loanid
        GROUP BY l.customerid
    )
    SELECT 
        c.customerid, 
        c.name, 
        c.phonenumber, 
        c.email, 
        COALESCE(a.account_count, 0) AS account_count, 
        COALESCE(a.total_balance, 0) AS total_balance, 
        COALESCE(l.loan_count, 0) AS loan_count, 
        COALESCE(l.total_loan_amount, 0) AS total_loan_amount, 
        COALESCE(p.payment_count, 0) AS payment_count, 
        COALESCE(p.total_payment_amount, 0) AS total_payment_amount,
        COALESCE(a.first_account_opened, NULL) AS first_account_opened, 
        COALESCE(a.latest_account_opened, NULL) AS latest_account_opened
    FROM 
        customer c
    LEFT JOIN 
        AccountSummary a ON c.customerid = a.customerid
    LEFT JOIN 
        LoanSummary l ON c.customerid = l.customerid
    LEFT JOIN 
        PaymentSummary p ON c.customerid = p.customerid
    WHERE 
        1=1 -- Placeholder for dynamic filters
    """

    # Collect filters from request arguments
    filters = []
    params = {}

    # Search Filter
    search = request.args.get('search', '').strip()
    if search:
        filters.append("(c.name ILIKE %(search)s OR c.email ILIKE %(search)s OR c.phonenumber ILIKE %(search)s)")
        params['search'] = f"%{search}%"

    # Balance Filters
    min_balance = request.args.get('min_balance')
    if min_balance:
        filters.append("COALESCE(SUM(a.balance), 0) >= %(min_balance)s")
        params['min_balance'] = min_balance

    max_balance = request.args.get('max_balance')
    if max_balance:
        filters.append("COALESCE(account_count, 0) <= %(max_balance)s")
        params['max_balance'] = max_balance

    num_of_account = request.args.get('num_of_account')
    if num_of_account:
        filters.append("a.account_count >= %(num_of_account)s")
        params['num_of_account'] = num_of_account


    # Loan Filters
    loan_status = request.args.get('loan_status')
    if loan_status:
        filters.append("l.status = %(loan_status)s")
        params['loan_status'] = loan_status

    min_loan_amount = request.args.get('min_loan_amount')
    if min_loan_amount:
        filters.append("l.total_loan_amount >= %(min_loan_amount)s")
        params['min_loan_amount'] = min_loan_amount

    max_loan_amount = request.args.get('max_loan_amount')
    if max_loan_amount:
        filters.append("l.total_loan_amount <= %(max_loan_amount)s")
        params['max_loan_amount'] = max_loan_amount

    # Payment Filters
    payment_status = request.args.get('payment_status')
    if payment_status:
        filters.append("lp.status = %(payment_status)s")
        params['payment_status'] = payment_status

    min_payment_amount = request.args.get('min_payment_amount')
    if min_payment_amount:
        filters.append("lp.amount >= %(min_payment_amount)s")
        params['min_payment_amount'] = min_payment_amount

    max_payment_amount = request.args.get('max_payment_amount')
    if max_payment_amount:
        filters.append("lp.amount <= %(max_payment_amount)s")
        params['max_payment_amount'] = max_payment_amount

    # Date Filters
    start_date = request.args.get('start_date')
    if start_date:
        filters.append("MIN(a.dateopened) >= %(start_date)s")
        params['start_date'] = start_date

    end_date = request.args.get('end_date')
    if end_date:
        filters.append("MAX(a.dateopened) <= %(end_date)s")
        params['end_date'] = end_date

    # Apply filters to the query
    if filters:
        AGGREGATE_QUERY += " AND " + " AND ".join(filters)

    # Order and limit the query
    AGGREGATE_QUERY += """
    ORDER BY 
        c.name;
    """

    # Execute query
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(AGGREGATE_QUERY, params)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    # Return the data or render template as needed
    return render_template('view_all_customer.html', data=data)

@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# View all accounts
@admin_bp.route('/view_all_accounts', methods=['GET', 'POST'])
def view_all_accounts():
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500

    cursor = conn.cursor()

    # Build the base query
    query = "SELECT AccountID, CustomerID, Balance, Currency, BranchID, Status FROM Account WHERE 1=1"
    filters = []

    # Collect filter values from request.args
    customer_id = request.args.get('customer_id')
    balance_comparison = request.args.get('balance_comparison')
    balance_value = request.args.get('balance_value')
    currency = request.args.get('currency')
    branch_id = request.args.get('branch_id')
    status = request.args.get('status')

    # Add conditions based on the filters
    if customer_id:
        query += " AND CustomerID = %s"
        filters.append(customer_id)
    if balance_comparison and balance_value:
        if balance_comparison == "over":
            query += " AND Balance > %s"
        elif balance_comparison == "under":
            query += " AND Balance < %s"
        filters.append(balance_value)
    if currency:
        query += " AND Currency = %s"
        filters.append(currency)
    if branch_id:
        query += " AND BranchID = %s"
        filters.append(branch_id)
    if status:
        query += " AND Status = %s"
        filters.append(status)

    # Execute the query
    cursor.execute(query, filters)
    accounts = cursor.fetchall()
    conn.close()

    return render_template('view_all_accounts.html', accounts=accounts)

# View all loan requests
@admin_bp.route('/approve_loan', methods=['GET'])
def approve_loan():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Loan WHERE Status = %s', ('W',))
        loan_requests = cursor.fetchall()
        conn.close()
        return render_template('approve_loan.html', loan_requests=loan_requests)
    else:
        return "Database connection error", 500
    
@admin_bp.route('/account_info', methods=['GET'])
def account_info():
    account_id = request.args.get('account_id')
    
    if not account_id:
        return "Account ID not provided", 400

    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500

    cursor = conn.cursor()

    # Query for detailed account information
    query = """
    SELECT *
    FROM Account
    WHERE AccountID = %s
    """
    cursor.execute(query, (account_id,))
    account_details = cursor.fetchone()

    query = """
        SELECT *
        FROM Loan
        WHERE CustomerID IN (
            SELECT CustomerID
            FROM Account
            WHERE AccountID = %s
        )
    """
    cursor.execute(query, (account_id,))
    loan_details = cursor.fetchall()  # Use fetchall() if expecting multiple rows


    query = """
        SELECT *
        FROM Creditcard
        WHERE Customerid IN
        (SELECT Customerid
         FROM Account
         WHERE AccountID = %s)
    """
    cursor.execute(query, (account_id,))
    creditcard_details = cursor.fetchone()

    conn.close()

    if not account_details:
        return f"No account found with Account ID {account_id}", 404

    return render_template('account_info.html', account=account_details, loans=loan_details, creditcards=creditcard_details)

# Approve loan request
@admin_bp.route('/approve_loan/<loan_id>', methods=['POST'])
def approve_single_loan(loan_id):
    """Approve a single loan and generate loan payments."""
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500

    cursor = conn.cursor()

    try:
        # Lock the loan row for update
        cursor.execute(
            '''
            SELECT principalamount, interestrate, duration, startdate
            FROM Loan
            WHERE loanid = %s AND status = %s
            FOR UPDATE
            ''',
            (loan_id, 'W')
        )
        loan_details = cursor.fetchone()

        if not loan_details:
            flash("Loan not found or already approved.", "danger")
            return redirect(url_for('admin.approve_loan'))

        # Extract loan details
        principal, rate, duration, start_date = loan_details
        print(f"Loan Details - Loan ID: {loan_id}, Principal: {principal}, Rate: {rate}, Duration: {duration}, Start Date: {start_date}")

        # Update loan status to 'A' (Approved)
        cursor.execute('UPDATE Loan SET status = %s WHERE loanid = %s', ('A', loan_id))

        # Generate loan payments
        monthly_rate = rate / 100.0 / 12
        monthly_payment = principal * monthly_rate * (1 + monthly_rate)**duration / ((1 + monthly_rate)**duration - 1)
        remaining_balance = principal
        payment_date = start_date

        print(f"Generating payments for Loan ID: {loan_id}, Monthly Payment: {monthly_payment}")

        for i in range(1, duration + 1):
            interest_paid = remaining_balance * monthly_rate
            principal_paid = monthly_payment - interest_paid
            # Shorten loan_id to ensure paymentid fits within 15 characters
            short_loan_id = loan_id[:10]
            payment_id = f"{short_loan_id}-{i:02}"

            # Insert loan payment record
            cursor.execute(
                '''
                INSERT INTO loanpayment (paymentid, loanid, paymentdate, amount, status, interestpaid, principlepaid)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''',
                (payment_id, loan_id, payment_date, monthly_payment, 'U', interest_paid, principal_paid)
            )

            print(f"Inserted Payment {payment_id} - Date: {payment_date}, Amount: {monthly_payment}")
            remaining_balance -= principal_paid
            payment_date += relativedelta(months=1)

        conn.commit()
        flash(f"Loan {loan_id} approved and payments generated successfully!", "success")

    except Exception as e:
        conn.rollback()
        print(f"Error approving loan {loan_id}: {e}")
        flash(f"Error approving loan {loan_id}.", "danger")

    finally:
        conn.close()

    return redirect(url_for('admin.approve_loan'))

# View all transactions
@admin_bp.route('/view_all_transactions')
def view_all_transactions():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Transaction')
        transactions = cursor.fetchall()
        conn.close()
        return render_template('view_all_transactions.html', transactions=transactions)
    else:
        return "Database connection error", 500

@admin_bp.route('/admin/import', methods=['GET', 'POST'])
def bulk_import():
    if request.method == 'GET':
        # Render the upload form
        return render_template('bulk_import.html')

    elif request.method == 'POST':
        # Handle file upload
        file = request.files.get('file')
        if not file or not file.filename.endswith('.csv'):
            return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400

        # Acquire the import lock
        if not import_lock.acquire(blocking=False):
            return jsonify({'error': 'Another import process is running. Please try again later.'}), 429

        try:
            # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Use write locks for tables being updated
            cursor.execute("LOCK TABLE customer IN EXCLUSIVE MODE;")
            cursor.execute("LOCK TABLE account IN EXCLUSIVE MODE;")

            # Read CSV file
            csv_data = csv.reader(file.stream)

            # Skip the header
            headers = next(csv_data, None)

            # Validate headers (example headers: customerid, name, email, phonenumber, etc.)
            expected_headers = ['customerid', 'name', 'phonenumber', 'email', 'gender', 'address', 'datejoined', 'birthday']
            if headers != expected_headers:
                return jsonify({'error': 'Invalid CSV format. Please check the header names.'}), 400

            # Insert data into the database
            for row in csv_data:
                try:
                    cursor.execute(
                        """
                        INSERT INTO customer (customerid, name, phonenumber, email, gender, address, datejoined, birthday)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (customerid) DO UPDATE
                        SET name = EXCLUDED.name, phonenumber = EXCLUDED.phonenumber, email = EXCLUDED.email,
                            gender = EXCLUDED.gender, address = EXCLUDED.address, datejoined = EXCLUDED.datejoined, birthday = EXCLUDED.birthday;
                        """,
                        row
                    )
                except Exception as e:
                    print(f"Error inserting row {row}: {e}")

            # Commit the transaction
            conn.commit()

            # Close connection
            cursor.close()
            conn.close()

            return render_template('bulk_import.html', message='Import successful!')        
        except Exception as e:
            # Rollback in case of error
            conn.rollback()
            return render_template('data_import.html', error=f"An error occurred: {str(e)}")
        finally:
            # Release the lock
            import_lock.release()


            admin_bp = Blueprint('admin_bp', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for displaying the CSV import page
@admin_bp.route('/import_customers', methods=['GET', 'POST'])
def import_customers():
    if request.method == 'POST':
        file = request.files['file']
        
        # Check if the file exists and is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Read the CSV data
            stream = io.StringIO(file.read().decode('utf-8'), newline=None)
            csv_reader = csv.DictReader(stream)
            
            # Connect to the database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert customer data from CSV
            for row in csv_reader:
                cursor.execute("""
                    INSERT INTO customer (customerid, name, phonenumber, email, gender, address, datejoined, birthday)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (customerid) DO NOTHING;
                """, (row['customerid'], row['name'], row['phonenumber'], row['email'], row['gender'], row['address'], row['datejoined'], row['birthday']))
            
            conn.commit()
            cursor.close()
            conn.close()

    return render_template('import_customers.html')