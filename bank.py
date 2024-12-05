from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from datetime import datetime
import uuid
from datetime import timedelta
from flask import Flask, session
from db import get_db_connection

bank_bp = Blueprint('bank', __name__)

@bank_bp.route('/branch_search', methods=['GET', 'POST'])
def branch_search():
    results = []
    if request.method == 'POST':
        # Collect input data from the form
        data = {
            'BankerID': request.form.get('BankerID'),
            'BranchID': request.form.get('BranchID'),
            'day': request.form.get('day')
        }
        
        # Get database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Build dynamic WHERE clause based on which fields are provided
        query = """
            SELECT bk.bankername, 
                    br.bankerid, 
                    br.branchid, 
                    br.location, 
                    br.phonenumber, 
                    oh.day, 
                    oh.starttime, 
                    oh.endtime
                FROM branch AS br 
                LEFT JOIN banker AS bk ON bk.bankerid = br.bankerid   -- Correct the join here
                LEFT JOIN openinghour AS oh ON oh.branchid = br.branchid
                WHERE 1=1

        """
        params = []

        # Add filters dynamically
        if data['BankerID']:
            query += " AND br.bankerid = %s"
            params.append(data['BankerID'])
        if data['BranchID']:
            query += " AND br.branchid = %s"
            params.append(data['BranchID'])
        if data['day']:
            query += " AND oh.day = %s"
            params.append(data['day'])

        # Order the results
        query += " ORDER BY br.branchid DESC;"

        # Execute the query with dynamic filters
        try:
            cur.execute(query, tuple(params))
            results = cur.fetchall()

        except Exception as e:
            return f"An error occurred: {e}", 500

        finally:
            cur.close()
            conn.close()

    # For GET requests, render the search form and pass the results to the template
    return render_template('branch_search.html', results=results)
