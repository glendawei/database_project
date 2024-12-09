# Overview  
This is the database final project for the NTUIM course. We implemented a bank system called **IMBANK** using PostgreSQL, Flask, and simple HTML.

# System Features

## User Functions
- **Account Registration**:  
   Register multiple accounts with custom type (e.g., savings) and currency (default: TWD). Approval required.  
- **Account Inquiry**:  
   View account details and transaction history.
- **Transactions**:  
   Perform transfers, payments, and receipts.  
- **Branch Inquiry**:  
   Access branch details (ID, address, phone, hours).  

-  **Loan Application**:  
   Apply for loans with terms set by the bank.  
-  **Credit Card Application**:  
   Request multiple cards; type chosen by user, others set by the bank.  
-  **Card Transactions**:  
   Make purchases within credit limits.  
- **Repayment**:  
   Repay loans or card debts in installments.

## Admin Functions
- **Import Users**:  
   Add new user data.  
-  **Manage Accounts**:  
   Approve, freeze, or adjust accounts.  
-  **Loan Setup**:  
   Set loan terms based on user credit.  
-  **Credit Card Management**:  
   Adjust limits and generate unique card numbers.  
-  **Repayment Tracking**:  
   Monitor repayment progress.  
 - **Transaction Inquiry**:  
   Review user transactions to enhance services.


# DEMO Video
# Development Environment
- macOS
- PostgreSQL: 16.4
- python 3.12.7
  - psycopg2: 2.9.10







# Execution Method  
1. Install the necessary libraries:  
   ```bash
   python app.py
   ```
   
2. run the project using the following command:
      ```bash
   python app.py
   ```


