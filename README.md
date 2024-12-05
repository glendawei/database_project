# User Module for Flask Application
https://docs.google.com/document/d/1vUcBH9AJ7KIe3GqVK4SHl4E-omphv1j7_So3s6gdaUY/edit?tab=t.0#heading=h.n6d2tudkftn6

## Overview
The user module is designed with multiple Flask Blueprints, each connecting to a PostgreSQL database. It provides essential functionalities for customers, including registration, login, account management, loans, credit cards, and other banking services. These modules ensure efficient management of customer accounts, transactions, loans, and credit card activities.
## Blueprints and Functionality
### 1. **Account and Loan Services Blueprint**
- **Account-related Services (user)**: 
  - Customers can register, log in, search for their balance, view transaction history, and perform transactions.
- **Loan Services**: 
  - Customers can apply for loans, check their loan status, and make payments. Loan approvals require admin intervention.
### 2. **Bank Information Search Blueprint (bank)**
- Customers can search for operational details about the bank, including the opening and closing times of each branch.
### 3. **Credit Card Blueprint (card)**
- Handles all credit card-related queries, including applications, status checks, and transaction history.
- Customers can apply for credit cards (approval required from admin). They can also search for their credit card transactions.
## Index Page
The index page serves as a landing page with links to the following sections:
- **Account Services**
- **Other Services (Loans and Credit Cards)**
- **About the Bank**
## Concurrency Handling
- To prevent concurrency issues, especially during account transactions and loan payments, **locks** are implemented in critical sections. This ensures data integrity when multiple users interact with the same account or loan.
- Additionally, we use **session keys** in Flask to ensure that different customers cannot override each other’s data. This helps maintain a unique session for each user, preventing conflicting changes or data corruption during concurrent actions.
## Search Optimization
- **Indexing**: Indexes are planned to accelerate searches, especially for bank information like branch operational hours. Although this feature is still pending implementation, it is intended to speed up database queries and improve performance.
# Admin Module for Flask Application
## Overview
The admin.py module is a Flask Blueprint that provides administrative functionality for managing customer data, accounts, loans, and transactions in a PostgreSQL-backed banking system. This module includes endpoints for data visualization, filtering, importing, and approving loans, as well as an admin dashboard for overall management.
## Features
1. Admin Dashboard
	•	Route: /admin_dashboard
	•	Purpose: Provides a central dashboard for administrative operations.
	•	Template: admin_dashboard.html
2. View All Customers
	•	Route: /view_all_customers
	•	Method: GET
	•	Description: Displays aggregated customer data, including accounts, loans, and payment details. Supports dynamic filtering and search.
	•	Template: view_all_customer.html
	•	Features:
	◦	Filter by customer name, email, phone number.
	◦	Filter by account balance, loan amount, or payment status.
	◦	Date filters for account creation and transactions.
3. View All Accounts
	•	Route: /view_all_accounts
	•	Methods: GET, POST
	•	Description: Lists account details with optional filters for customer ID, balance, currency, branch, and status.
	•	Template: view_all_accounts.html
4. Approve Loans
	•	Routes:
	◦	/approve_loan (GET): View pending loan requests.
	◦	/approve_loan/<loan_id> (POST): Approve a specific loan and generate payment schedules.
	•	Templates:
	◦	approve_loan.html
	•	Features:
	◦	Approve loans in "Waiting" status.
	◦	Automatically calculate and generate monthly payment schedules.
5. Account Information
	•	Route: /account_info
	•	Method: GET
	•	Description: Fetches detailed account, loan, and credit card information for a specific account ID.
	•	Template: account_info.html
6. View All Transactions
	•	Route: /view_all_transactions
	•	Method: GET
	•	Description: Lists all transactions in the system.
	•	Template: view_all_transactions.html
7. Bulk Import Customers
	•	Routes:
	◦	/admin/import (GET, POST): Bulk import customer data from a CSV file.
	◦	/import_customers (GET, POST): Alternate route for CSV import.
	•	Templates:
	◦	bulk_import.html, import_customers.html
	•	Features:
	◦	Supports conflict resolution with ON CONFLICT to update existing records.
	◦	Validates CSV headers before import.
## Configuration
Allowed File Types
	•	Only .csv files are supported for bulk import.
	•	Configuration: ALLOWED_EXTENSIONS = {'csv'}
	•	
## Indexing
The following PostgreSQL indices are created for optimization:
	•	idx_account_customerid
	•	idx_account_dateopened
	•	idx_account_balance
## Locking Mechanisms in the System
The system employs a combination of application-level and database-level locking to ensure data consistency and integrity during concurrent operations. Application-level locking is implemented using a mutual exclusion mechanism (import_lock) to prevent multiple users from initiating overlapping data import processes. This ensures that only one bulk import operation can run at any given time, mitigating the risk of data corruption or race conditions.
On the database side, SQL LOCK TABLE statements are used to secure exclusive access to critical tables like customer and account during bulk operations. This prevents other transactions from reading or modifying these tables while data import or update processes are in progress. By acquiring these locks, the system ensures that data remains consistent even in high-concurrency environments. To minimize the potential impact on system performance, locks are released promptly after the operation concludes. These locking strategies collectively provide robust safeguards against data conflicts and maintain the integrity of operations in a multi-user environment.

## DEMO Video
[![Watch the video](https://i.sstatic.net/Vp2cE.png)](https://youtu.be/vt5fpE0bzSY)







