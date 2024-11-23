import logging
from flask import flash
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import psycopg2
from datetime import datetime, timedelta
import uuid
from dateutil.relativedelta import relativedelta
from db import get_db_connection
from flask import Blueprint


admin_bp = Blueprint('admin', __name__)



@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# View all accounts
@admin_bp.route('/view_all_accounts')
def view_all_accounts():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT AccountID, CustomerID, Balance, Currency, BranchID FROM Account')
        accounts = cursor.fetchall()
        conn.close()
        return render_template('view_all_accounts.html', accounts=accounts)
    else:
        return "Database connection error", 500

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

# Approve loan request
@admin_bp.route('/approve_loan/<loan_id>', methods=['POST'])
def approve_single_loan(loan_id):
    """Approve a single loan and generate loan payments."""
    conn = get_db_connection()
    if not conn:
        return "Database connection error", 500

    cursor = conn.cursor()

    try:
        # Fetch loan details for the given loan_id
        cursor.execute(
            'SELECT principalamount, interestrate, duration, startdate FROM Loan WHERE loanid = %s AND status = %s',
            (loan_id, 'W')
        )
        loan_details = cursor.fetchone()

        if not loan_details:
            flash("Loan not found or already approved.", "danger")
            return redirect(url_for('admin.admin.approve_loan'))

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


