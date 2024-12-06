import datetime  # 主匯入 datetime 模組
from flask import Blueprint, request, render_template, redirect, url_for, jsonify, session
from db import get_db_connection
from faker import Faker
import random
from datetime import datetime, timedelta

card_bp = Blueprint('card', __name__)  # Define the blueprint for user routes


import random
fake = Faker()

def generate_card_id():
    id = fake.bothify(text ='????###########')
    return id[:15]
        
# Luhn algorithm to validate credit card number
def luhn_algorithm(card_number):
    total = 0
    reverse_digits = card_number[::-1]
    
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:  # Double every second digit starting from the right
            n *= 2
            if n > 9:
                n -= 9
        total += n
    
    return total % 10 == 0

# Generate a valid credit card number using Luhn's algorithm
def generate_credit_card_number(card_type='V', length=16):
    # Define prefixes for different card types
    prefixes = {
        'V': '4',  # Visa starts with 4
        'M': '5',  # MasterCard starts with 5
        'A': '34', # American Express starts with 34
        'D': '6011', # Discover starts with 6011
        'J': '35',  # JCB starts with 35
        'U': '62',  # UnionPay starts with 62
    }
    
    # Get the prefix for the selected card type
    prefix = prefixes.get(card_type, '4')  # Default to Visa if card type is not found
    
    # Generate a valid credit card number with the selected prefix
    while True:
        # Generate the first part of the card number (prefix + random digits)
        card_number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(length - len(prefix) - 1)])
        
        # Calculate the Luhn check digit
        check_sum = 0
        for i in range(length - 1):
            digit = int(card_number[i])
            if (length - i - 1) % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            check_sum += digit
        
        # Calculate the check digit to make the total divisible by 10
        check_digit = (10 - (check_sum % 10)) % 10
        card_number = card_number + str(check_digit)
        
        # Validate the card number
        if luhn_algorithm(card_number):
            return card_number


@card_bp.route('/credit_card', methods=['GET', 'POST'])
def credit_card():
    if request.method == 'POST':
        # Get today's date and set as IssueDate
        issue_date = datetime.today()
        expiry_date = issue_date + timedelta(days=7*365)  # Add 7 years to the IssueDate (approximate)

        # Extract data from form
        data = {
            'CustomerID': request.form.get('CustomerID'),
            'BranchID': request.form.get('BranchID'),
            'IssueDate': issue_date.strftime('%Y-%m-%d'),  # Default to today's date
            'ExpiryDate': expiry_date.strftime('%Y-%m-%d'),  # Set ExpiryDate to 7 years after IssueDate
            'InterestRate': 0.1,
            'Limit': 50000,
            'Status': 'W',
            'Type': request.form.get('Type'),
            'CVN': str(random.randint(100, 999)).zfill(3),  # Ensure CVN is 3 digits
            'lastupdate': issue_date.strftime('%Y-%m-%d'), 
           
        }
        card_type=  data['Type']

        data['Number'] = generate_credit_card_number(card_type) 

        # Generate CardID using the CustomerID
        data['CardID'] = generate_card_id()

 

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
                                        InterestRate, CardLimit, Status, Type, CVN, Number, lastupdate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['CardID'], data['CustomerID'], data['BranchID'], data['IssueDate'], 
                data['ExpiryDate'], data['InterestRate'], data['Limit'], data['Status'],
                data['Type'], data['CVN'], data['Number'], data['lastupdate']
            ))


            conn.commit()
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cur.close()
            conn.close()

        # Instead of redirecting, we return a response with the card details
        return render_template('card_result.html', card=data)

    return render_template('credit_card.html')


@card_bp.route('/clogin', methods=['GET', 'POST'])
def clogin():
    if request.method == 'POST':
        card_id = request.form.get('CardID')

        # Validate the CardID against the database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM CREDITCARD 
            WHERE CardID = %s
            AND Status = 'A'  -- Ensure the card is active
            AND ExpiryDate > CURRENT_DATE  -- Ensure the card is not expired
        """, (card_id,))
        card = cur.fetchone()
        cur.close()
        conn.close()

        if card:
            session['card_id'] = card_id  # Store the CardID in session
            return redirect(url_for('card.cdashboard'))  # Redirect to the dashboard page

        return jsonify({"error": "Invalid CardID or the card is inactive/expired"}), 400

    return render_template('clogin.html')


@card_bp.route('/cdashboard', methods=['GET'])
def cdashboard():
    # Check if the user is logged in
    if 'card_id' not in session:
        return redirect(url_for('card.clogin'))

    card_id = session['card_id']
    return render_template('cdashboard.html', card_id=card_id)

@card_bp.route('/ctransactions', methods=['GET', 'POST'])
def ctransactions():
    # Check if the user is logged in
    if 'card_id' not in session:
        print("Card ID not in session!")
        return redirect(url_for('card.login'))

    card_id = session['card_id']
    transactions = []

    if request.method == 'POST':
        # Get search criteria from the form
        date_from = request.form.get('DateFrom')
        date_to = request.form.get('DateTo')
        print(f"DateFrom: {date_from}, DateTo: {date_to}")

        # Build the query dynamically based on inputs
        query = "SELECT * FROM CREDITCARDTRANSACTION WHERE CreditCardID = %s"
        params = [card_id]

        if date_from:
            query += " AND Date >= %s"
            params.append(date_from)
        if date_to:
            query += " AND Date <= %s"
            params.append(date_to)
        
        print(f"Query: {query}, Params: {params}")

        # Execute the query
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(query, tuple(params))
            transactions = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
            return "Database error, please try again later."
     


    return render_template('ctransactions.html', transactions=transactions)

# Function to generate monthly bills
def generate_monthly_bills():
    print("MMMMMM")
    today = datetime.today()
    first_day_of_this_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_this_month - timedelta(days=1)
    
    try:
        # Fetch last update from creditcard table
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT lastupdate FROM creditcard WHERE cardid = %s", (session['card_id'],))
        lastupdate = cur.fetchone()[0]
    

        print(f"Last update: {lastupdate}")
        print(f"Last day of last month: {last_day_of_last_month}")

        # Query to calculate total transaction amounts for each credit card in the last month
        cur.execute("""
            SELECT CreditCardID, 
                TO_CHAR(Date, 'YYYY-MM') AS Month, 
                SUM(Amount) 
            FROM CREDITCARDTRANSACTION
            WHERE Date BETWEEN %s AND %s
            GROUP BY CreditCardID, Month
            ORDER BY Month;

        """, (lastupdate, last_day_of_last_month))
        print("moooooo")
        
        transactions = cur.fetchall()

        # Insert or update the monthly bills
        for transaction in transactions:
            card_id, bill_month, total_amount = transaction

            # Insert or update monthlybill table
            cur.execute("""
                INSERT INTO monthlybill (CreditCardID, BillMonth, TotalAmount, PaidAmount)
                VALUES (%s, %s, %s, 0.00)  -- Set initial PaidAmount to 0
                ON CONFLICT (CreditCardID, BillMonth)  -- Specify the conflict target (the columns that make the row unique)
                DO UPDATE SET 
                    TotalAmount = EXCLUDED.TotalAmount,  -- Update the TotalAmount with the new value
                    PaidAmount = EXCLUDED.PaidAmount;  -- Ensure PaidAmount is updated correctly (if needed)
            """, (card_id, bill_month, total_amount))

        # Update the last update date for the card
        cur.execute("""
            UPDATE creditcard
            SET lastupdate = %s
            WHERE cardid = %s
       
        """, (first_day_of_this_month, session['card_id']))

        conn.commit()
        cur.close()
        conn.close()
        print("oooo")


    except Exception as e:
        print(f"Error generating monthly bills: {e}")


def generate_unique_payment_id():
  id = fake.bothify(text ='???????#######')
  return id


from decimal import Decimal

@card_bp.route('/repayment', methods=['GET', 'POST'])
def repayment():
    if 'card_id' not in session:
        print("請先登入以進行還款操作。", "warning")
        return redirect(url_for('card.login'))

    card_id = session['card_id']
    conn = get_db_connection()

    with conn.cursor() as cur:
        # 生成月帳單
        generate_monthly_bills()
        
        # 查詢所有未付清的帳單
        cur.execute("""
            SELECT BillMonth, totalAmount, paidAmount, totalAmount - paidAmount AS remainingAmount
            FROM MONTHLYBILL 
            WHERE CreditCardID = %s AND totalAmount - paidAmount > 0
            ORDER BY BillMonth ASC
        """, (card_id,))
        bills = cur.fetchall()

    if request.method == 'POST':
        bill_month = request.form.get('bill_month')
        payment_amount = request.form.get('payment_amount',type = int)

        m = request.form.get('method')

        if not bill_month or payment_amount is None:
            print("請提供帳單月份和還款金額。", "danger")
            return render_template('repayment.html', bills=bills)

        try:
            with conn.cursor() as cur:
                # 檢查指定月份帳單是否存在
                cur.execute("""
                    SELECT totalAmount, paidAmount
                    FROM MONTHLYBILL
                    WHERE CreditCardID = %s AND BillMonth = %s
                """, (card_id, bill_month))
                bill = cur.fetchone()

                if not bill:
                    print("找不到指定月份的帳單。", "danger")
                else:
                    total_amount, paid_amount = bill
                    remaining_amount = total_amount - paid_amount

                    if payment_amount > remaining_amount:
                        print(f"還款金額超過剩餘金額 (剩餘: {remaining_amount})。", "danger")
                    else:
                        # 更新帳單還款金額
                        cur.execute("""
                            UPDATE MONTHLYBILL
                            SET paidAmount = paidAmount + %s
                            WHERE CreditCardID = %s AND BillMonth = %s
                        """, (payment_amount, card_id, bill_month))

                        paymentid =generate_unique_payment_id()

                        # 紀錄還款操作
                        date = datetime.now().strftime('%Y-%m-%d')
                        cur.execute("""
                            INSERT INTO CREDITCARDPAYMENT (PaymentID, CreditCardID, Date, Amount, Status, Method, RemainingBalance)
                            VALUES (%s, %s, %s, %s, 'A', %s, %s)
                        """, (paymentid, card_id, date, payment_amount, m,remaining_amount - payment_amount))


                        conn.commit()
                        print("還款成功！", "success")
        except Exception as e:
            conn.rollback()
            print(f"發生錯誤：{str(e)}", "danger")

        # 重新載入未付清帳單
        with conn.cursor() as cur:
            cur.execute("""
                SELECT BillMonth, totalAmount, paidAmount, totalAmount - paidAmount AS remainingAmount
                FROM MONTHLYBILL 
                WHERE CreditCardID = %s AND totalAmount - paidAmount > 0
                ORDER BY BillMonth ASC
            """, (card_id,))
            bills = cur.fetchall()

    return render_template('repayment.html', bills=bills)



@card_bp.route('/clogout', methods=['GET'])
def clogout():
    # Clear the session (log the user out)
    session.pop('card_id', None)
    return redirect(url_for('card.clogin'))  # Redirect to the login page
