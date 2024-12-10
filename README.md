# Overview  
This is the database final project for the NTUIM course. We implemented a bank system called **IMBANK** using PostgreSQL, Flask, and simple HTML. **IMBANK** is an online platform designed to help users manage financial services conveniently without visiting a physical bank. It aims to address the inconvenience caused by traditional banking hours conflicting with the schedules of working professionals and students.

# System Features


The platform supports two user roles: User and Admin. Users can create multiple accounts across different banks, manage accounts, and perform services like loans, credit card management, and online transactions.  Admins, representing bank staff, can manage loan services, access account details, and review transaction records .

## User Functions in the System

1. **Register Bank Account:**  
   Users can register online or in person by providing customer ID, account ID, password, branch code, account balance, account type (default: savings), and currency (default: NTD).

2. **Account Login:**  
   Log in using account ID and password to:  
   - Check balance.  
   - View transaction records (deposits, transfers).  
   - Manage transfers (set recipient and amount).

3. **Bank Info Lookup:**  
   Search by bank ID, branch ID, or day to find branch details, including address, phone, and hours.

4. **Loan Application:**  
   Apply for loans by providing customer ID, birthdate, loan type, amount, and duration. Approval and interest rates are managed by the bank.

5. **Loan Repayment:**  
   Search approved loans and repay. The system calculates and updates principal and interest paid.

6. **Credit Card Application:**  
   Apply for a credit card by providing customer ID, branch code, and card type (e.g., Visa). Approval is handled by the bank.

7. **Credit Card Services:**  
   Log in to:  
   - View transactions (filter by date).  
   - Pay outstanding bills (select month and amount).


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
   pip install requirements.txt
   ```
   
2. run the project using the following command:
      ```bash
   python app.py
   ```


