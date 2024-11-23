
from flask import Blueprint, request, render_template, redirect, url_for, jsonify

from datetime import datetime
import uuid
from datetime import timedelta
from flask import Flask, session
from db import get_db_connection
bank_bp = Blueprint('bank', __name__)  # Define the blueprint for user routes


@bank_bp.route('/branch_search', methods=['GET', 'POST'])
def branch_search():
    if request.method == 'POST':
        # Collect input data from the form
        data = {
            'BankerID': request.form.get('BankerID'),  # Corrected missing key
            'day': request.form.get('day')  # Added day field
        }
        
        # Check if both inputs are provided
        if not data['BankerID'] or not data['day']:
            return "BankerID and day are required fields.", 400
        
        # Get database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Execute SQL query
        try:
            cur.execute("""
                SELECT br.branchid, br.location, br.phonenumber, oh.starttime, oh.endtime
                FROM branch AS br
                LEFT JOIN openinghour AS oh ON oh.branchid = br.branchid
                WHERE br.bankerid = %s AND oh.day = %s
                ORDER BY br.branchid DESC;
            """, (data['BankerID'], data['day']))
            
            # Fetch results
            results = cur.fetchall()
            # Return results as a JSON response
            return jsonify(results)

        except Exception as e:
            # Handle any errors during SQL execution
            return f"An error occurred: {e}", 500

        finally:
            # Close database connection
            cur.close()
            conn.close()
    
    # For GET requests, render the search form
    return render_template('branch_search.html')

