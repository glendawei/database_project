import logging
from flask import Blueprint, request, render_template, redirect, url_for, jsonify

from datetime import datetime
import uuid
from datetime import timedelta
from flask import Flask, session
from db import get_db_connection
import random
card_bp = Blueprint('card', __name__)  # Define the blueprint for user routes


import random
import random

def generate_card_id(customer_id):
    retries = 0
    cardNum = 14
    ranNum = 10
    round = 1
    maxround = 5

    while round < maxround:
        conn = get_db_connection()
        cur = conn.cursor()

        # Base card id is the first `cardNum` digits of the customer_id
        base_card_id = customer_id[:cardNum]
        
        # Calculate the number of random digits to append based on the current round
        suffix_length = round  # Number of random digits increases with each round
        max_retries = ranNum**suffix_length
        
        # Generate a random suffix with enough digits to fill the required length
        suffix = str(random.randint(0, max_retries-1)).zfill(suffix_length)
        
        # Combine the base and suffix to form the final card ID
        card_id = base_card_id + suffix
        
        # Check if the card_id exists in the database
        cur.execute("SELECT EXISTS(SELECT 1 FROM CREDITCARD WHERE CardID = %s  )", (card_id,))
        exists = cur.fetchone()[0]
        cur.close()
        
        # If the CardID does not exist, return it
        if not exists:
            return card_id
        
        # Retry logic
        retries += 1
        if retries >= max_retries:
            cardNum -= 1  # Reduce the base card number length if retries exceed max
            retries = 0
            round += 1
    
    # If no unique CardID is found within the retry limit, raise an exception
    raise Exception("Failed to generate a unique CardID after {} retries.".format(max_retries))
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
           
        }
        card_type=  data['Type']

        data['Number'] = generate_credit_card_number(card_type) 

        # Generate CardID using the CustomerID
        data['CardID'] = generate_card_id(data['CustomerID'])

 

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
                                         InterestRate, CardLimit, Status, Type, CVN, Number)
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
        print(f"Transactions: {transactions}")


    return render_template('ctransactions.html', transactions=transactions)

@card_bp.route('/clogout', methods=['GET'])
def clogout():
    # Clear the session (log the user out)
    session.pop('card_id', None)
    return redirect(url_for('card.clogin'))  # Redirect to the login page
