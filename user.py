
import logging
from flask import Blueprint, request, render_template, redirect, url_for, jsonify

from datetime import datetime
import uuid
from datetime import timedelta
from flask import Flask, session
from db import get_db_connection
user_bp = Blueprint('user', __name__)  # Define the blueprint for user routes


# Home page
@user_bp.route('/')
def index():
    return render_template('index.html')  # 確保該模板存在並且路徑正確 # Home page with 4 buttons: Register, Login, Loans, Credit Card

# Register Account
@user_bp.route('/register_account', methods=['GET', 'POST'])
def register_account():
    if request.method == 'POST':
        # 提取表單數據，設定預設值
        data = {
            'AccountID': request.form.get('AccountID'),
            'AccountType': request.form.get('AccountType', 'UK'),
            'BranchID': request.form.get('BranchID'),
            'DateOpened': datetime.now().strftime('%Y-%m-%d'),  # 預設為今天日期
            'InterestRate': request.form.get('InterestRate', 0.1),  # 轉換為 int
            'Status': request.form.get('Status', 'C'),  # 預設為 0，轉換為 int
            'CustomerID': request.form.get('CustomerID'),
            'Balance': int(request.form.get('Balance', 0)),  # 預設為 0，轉換為 bigint
            'Currency': request.form.get('Currency', 'TWD'),  # 預設為 TWD
            'OverdraftLimit': int(request.form.get('OverdraftLimit', 0)),  # 預設為 0，轉換為 bigint
            'Password': request.form.get('Password')
        }

        # 檢查必要欄位是否缺失
        required_fields = ['AccountID', 'AccountType', 'BranchID', 'CustomerID', 'Password']
        if not all(data[field] for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            # 連接資料庫
            conn = get_db_connection()
            cur = conn.cursor()

            # 插入資料到 ACCOUNT 表
            cur.execute("""
                INSERT INTO ACCOUNT (
                    AccountID, AccountType, Balance, BranchID, Currency, 
                    OverdraftLimit, DateOpened, InterestRate, Status, CustomerID, Password
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['AccountID'], data['AccountType'], data['Balance'], data['BranchID'], 
                data['Currency'], data['OverdraftLimit'], data['DateOpened'], 
                data['InterestRate'], data['Status'], data['CustomerID'], data['Password']
            ))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cur.close()
            conn.close()

        # 成功後重定向到首頁
        return redirect(url_for('user.index'))

    # GET 請求時渲染表單
    return render_template('register_account.html')

# Login
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Generate unique session ID for each tab
        tab_session_id = str(uuid.uuid4())

        # Clear any existing session
        if 'AccountID' in session:
            session.pop('AccountID', None)

        # From form
        data = {
            'AccountID': request.form.get('AccountID'),
            'Password': request.form.get('Password')
        }

        try:
            # Database connection and login logic here
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "SELECT password FROM ACCOUNT WHERE AccountID = %s"
            cursor.execute(query, (data['AccountID'],))
            result = cursor.fetchone()

            if result and result[0] == data['Password']:
                # Store unique session for this tab
                session['AccountID'] = data['AccountID']
                session['tab_session_id'] = tab_session_id  # Unique session ID for this tab
                session.modified = True  # Mark session as modified
                return render_template('afterlogin.html')
            else:
                return render_template('login.html', error="Invalid credentials")

        except Exception as e:
            logging.error(f"Error during login: {str(e)}")
            return render_template('login.html', error="An unexpected error occurred. Please try again.")
        finally:
            if conn:
                conn.close()

    return render_template('login.html')


# After login page (check balance, transaction record, and perform transaction)
@user_bp.route('/afterlogin')
def afterlogin():
    # Ensure that both AccountID and tab_session_id are present and match
    if 'AccountID' not in session or 'tab_session_id' not in session:
        return redirect(url_for('user.index'))  # Redirect to home if not logged in or session expired

    # Optional: further validation can be added to verify the tab_session_id here

    return render_template('afterlogin.html') # Contains buttons for checking balance, transaction record, and transaction

@user_bp.route('/check_balance')
def check_balance():
    # Ensure that both AccountID and tab_session_id are present and match
    if 'AccountID' not in session or 'tab_session_id' not in session:
        return redirect(url_for('user.index'))  # Redirect to home if not logged in or session expired

    account_id = session['AccountID']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT Balance FROM ACCOUNT WHERE AccountID = %s", (account_id,))
    account = cur.fetchone()
    conn.close()

    return render_template('check_balance.html', balance=account[0])


@user_bp.route('/check_transaction_record')
def check_transaction_record():
    # Ensure that both AccountID and tab_session_id are present and match
    if 'AccountID' not in session or 'tab_session_id' not in session:
        return redirect(url_for('user.index'))  # Redirect to home if not logged in or session expired

    account_id = session['AccountID']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT TransactionID, transactiontype, transactionaccount, Amount, description FROM TRANSACTION WHERE AccountID = %s", (account_id,))
    transactions = cur.fetchall()
    conn.close()

    return render_template('check_transaction_record.html', transactions=transactions)

@user_bp.route('/logout')
def logout():
    session.pop('AccountID', None)  # Remove the AccountID from session
    session.pop('tab_session_id', None)  # Remove the tab session ID from session
    return redirect(url_for('user.index'))  # Redirect to home page

@user_bp.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    # Ensure that both AccountID and tab_session_id are present and match
    if 'AccountID' not in session or 'tab_session_id' not in session:
        return redirect(url_for('user.index'))  # Redirect to home if not logged in or session expired

    if request.method == 'POST':
        data = {
            'Status': request.form.get('Status', 1),
            'Amount': request.form.get('Amount'),
            'TransactionAccount': request.form.get('TransactionAccountID')  
        }

        try:
            data['RequestTime'] = datetime.now().strftime('%H:%M:%S')
            data['CompleteTime'] = datetime.now().strftime('%H:%M:%S')

        except ValueError:
            return jsonify({"error": "Invalid time format. Use HH:MM:SS"}), 400
        
        transaction_id = f"{session['AccountID']}_{int(datetime.now().timestamp())}_T"
        data['TransactionID'] = transaction_id
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO TRANSACTION (
                    TransactionID, TransactionType, Status, Description, 
                    RequestTime, CompleteTime, Amount, AccountID, transactionaccount  
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['TransactionID'], 'T', data['Status'], request.form.get('Description'), 
                data['RequestTime'], data['CompleteTime'], data['Amount'], 
                session['AccountID'], data['TransactionAccount']  
            ))

            transaction_id = f"{session['AccountID']}_{int(datetime.now().timestamp())}_R"
            data['TransactionID'] = transaction_id

            cur.execute("""
                INSERT INTO TRANSACTION (
                    TransactionID, TransactionType, Status, Description, 
                    RequestTime, CompleteTime, Amount, AccountID, transactionaccount
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['TransactionID'], 'R', data['Status'], request.form.get('Description'), 
                data['RequestTime'], data['CompleteTime'], data['Amount'], 
                data['TransactionAccount'], session['AccountID']  
            ))
            # update the balance
            cur.execute("""
                UPDATE ACCOUNT
                SET Balance = Balance - %s
                WHERE AccountID = %s
            """, (data['Amount'], session['AccountID']))
            cur.execute("""
                UPDATE ACCOUNT
                SET Balance = Balance + %s
                WHERE AccountID = %s
            """, (data['Amount'], data['TransactionAccount']))

            conn.commit()
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('user.afterlogin'))  # Redirect to afterlogin page after successful transaction

    return render_template('add_transaction.html')




@user_bp.route('/loan', methods=['GET', 'POST'])
def loan():
    if request.method == 'POST':
        # Extract data from form
        data = {
            'LoanType': request.form.get('LoanType'),
            'PrincipalAmount': request.form.get('PrincipalAmount'),
          
            'Duration': request.form.get('Duration'),
            'CustomerID': request.form.get('CustomerID')
        }
    
        data['LoanID'] = str(uuid.uuid4()).replace("-", "")[:15]  
        data['InterestRate'] = 10
        data['StartDate'] = datetime.now().strftime('%Y-%m-%d')  

        data['Status']= 'W'

        required_fields = ['LoanID', 'LoanType', 'PrincipalAmount', 'Status', 'InterestRate', 
                            'StartDate', 'Duration', 'CustomerID']
        if not all(data[field] for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO LOAN (LoanID, LoanType, PrincipalAmount, Status, 
                                   InterestRate, StartDate, Duration, CustomerID)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['LoanID'], data['LoanType'], data['PrincipalAmount'], data['Status'], 
                data['InterestRate'], data['StartDate'], data['Duration'], data['CustomerID']
            ))

            conn.commit()
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('user.index'))  

    return render_template('loan.html')  


@user_bp.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':

        customer_id = request.form['CustomerID']
      
        if customer_id:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM LOAN
                WHERE CustomerID = %s
            """, (customer_id,))
            loans = cur.fetchall()
            print(f"Loans found: {loans}")  # Debug print
            session['CustomerID'] = customer_id
            cur.close()
            conn.close()
            return redirect(url_for('user.search_loan'))
        else:
            return "Customer ID is required", 400
    return render_template('customer_login.html')

def get_loans_for_customer(customer_id):

    conn = None
    cur = None
    loans = []

    try:
        # 獲取資料庫連線
        conn = get_db_connection()
        cur = conn.cursor()

        # 執行查詢
        query = """
        SELECT LoanID, LoanType, PrincipalAmount, InterestRate, StartDate, Duration
        FROM LOAN
        WHERE CustomerID = %s
        """
        cur.execute(query, (customer_id,))

        # 獲取查詢結果
        loans = cur.fetchall()

    except Exception as e:
        print(f"查詢貸款時出現錯誤: {e}")
    finally:
        # 確保關閉游標和連線
        if cur:
            cur.close()
        if conn:
            conn.close()

    return loans

@user_bp.route('/search_loan', methods=['GET', 'POST'])
def search_loan():
    if request.method == 'GET':
        # Render search page
        customer_id = session.get('CustomerID')
        if not customer_id:
            return redirect(url_for('user.customer_login'))

        # Query loans and store in session
        loans = get_loans_for_customer(customer_id)
        session['loans'] = loans  # Save loans in session

    elif request.method == 'POST':
        # Extract loan details from form data
        loan_id = request.form.get('loan_id')
        loan_type = request.form.get('loan_type')
        amount = request.form.get('amount')
        interest_rate = request.form.get('interest_rate')
        start_date = request.form.get('start_date')
        term_months = request.form.get('term_months')

        # Pack the extracted details into a tuple
        selected_loan = (loan_id, loan_type, amount, interest_rate, start_date, term_months)
  
        session['selected_loan'] = selected_loan

        return redirect(url_for('user.loan_payment'))


    return render_template('search_loan.html', loans=session.get('loans', []))



@user_bp.route('/loan_payment', methods=['GET', 'POST'])
def loan_payment():
    # Get the loan details from the session
    loan_details = session.get('selected_loan')

    if loan_details is None:
        print("No loan details in session.")
        return redirect(url_for('user.search_loan'))  # Redirect if no loan details found in the session
    
    loan_id, loan_type, amount, interest_rate, start_date, term_months = loan_details

    if request.method == 'GET':
        # Directly passing the loan details to the template
        return render_template('loan_payment.html', loan=(loan_id, amount, interest_rate))

    elif request.method == 'POST':
        # Get payment amount from the form
        payment_amount = request.form.get('PaymentAmount')

        if not payment_amount:
            print("Payment amount not provided.")
            return jsonify({"message": "Payment amount is required"}), 400

        try:
            # Ensure the payment amount is a float
            payment_amount = float(payment_amount)

            # Calculate interest and principal paid
            interest_paid = (float(interest_rate) / 100) * payment_amount
            principal_paid = payment_amount - interest_paid

            # Generate payment ID and payment date
            payment_id = str(uuid.uuid4()).replace("-", "")[:15]  # Optionally keep full UUID
            payment_date = datetime.now().strftime('%Y-%m-%d')

            # Database connection and operations
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Insert payment into LOANPAYMENT table
                    cur.execute("""
                        INSERT INTO LOANPAYMENT (PaymentID, LoanID, PaymentDate, Amount, Status, InterestPaid, PrinciplePaid)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (payment_id, loan_id, payment_date, payment_amount, 'C', interest_paid, principal_paid))

                    # Update the principal amount in the LOAN table
                    cur.execute("""
                        UPDATE LOAN
                        SET PrincipalAmount = PrincipalAmount - %s
                        WHERE LoanID = %s
                    """, (principal_paid, loan_id))

                    conn.commit()
                    session.pop('selected_loan', None)  # Remove CustomerID from session


            return redirect(url_for('user.search_loan'))

        except ValueError:
            print("Invalid payment amount.")
            return jsonify({"message": "Invalid payment amount"}), 400
        except Exception as e:

            print(f"Error processing payment: {e}")
            return jsonify({"message": "Error processing payment"}), 500




@user_bp.route('/customer_logout')
def customer_logout():
    session.pop('CustomerID', None)  # Remove CustomerID from session
    return redirect(url_for('user.customer_login')) 




#----------------------------------------------------------------------------


@user_bp.route('/credit_card', methods=['GET', 'POST'])
def credit_card():
    if request.method == 'POST':
        # Extract data from form
        data = {
            'CardID': request.form.get('CardID'),
            'CustomerID': request.form.get('CustomerID'),
            'BranchID': request.form.get('BranchID'),
            'IssueDate': request.form.get('IssueDate'),
            'ExpiryDate': request.form.get('ExpiryDate'),
            'InterestRate': request.form.get('InterestRate'),
            'Limit': request.form.get('Limit'),
            'Status': request.form.get('Status'),
            'Type': request.form.get('Type'),
            'CVN': request.form.get('CVN'),
            'Number': request.form.get('Number')
        }

        # Validate required fields
        required_fields = ['CardID', 'CustomerID', 'BranchID', 'IssueDate', 'ExpiryDate', 
                            'InterestRate', 'Limit', 'Status', 'Type', 'CVN', 'Number']
        if not all(data[field] for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate date format for IssueDate and ExpiryDate
        try:
            datetime.strptime(data['IssueDate'], '%Y-%m-%d')
            datetime.strptime(data['ExpiryDate'], '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Validate InterestRate and Limit are integers
        try:
            int(data['InterestRate'])
            int(data['Limit'])
        except ValueError:
            return jsonify({"error": "InterestRate and Limit must be integers"}), 400

        # Insert into CREDIT_CARD table
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO CREDITCARD (CardID, CustomerID, BranchID, IssueDate, ExpiryDate, 
                                         InterestRate, Limit, Status, Type, CVN, Number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['CardID'], data['CustomerID'], data['BranchID'], data['IssueDate'], 
                data['ExpiryDate'], data['InterestRate'], data['Limit'], data['Status'],
                data['Type'], data['CVN'], data['Number']
            ))

            conn.commit()
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('user.index'))  

    return render_template('credit_card.html')  

# --------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------

