# Overview  
This is the database final project for the NTUIM course. We implemented a bank system called **I’m Bank** using PostgreSQL, Flask, and simple HTML. **I’m Bank** is a platform that provides various online financial services for both banks and customers. Its primary purpose is to enable customers of different banks to manage their personal bank accounts, access account information, and utilize a range of financial services.

# System Features


The platform supports two user roles: **User** and **Admin**. Users, representing customers, can access key services offered by the bank, including those related to loans, account management, and credit card services. Admins, who represent the bank staff, are responsible for managing loan services, accessing account details, and reviewing transaction records.

- ## User Functions in the System

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


- ## Admin Functions
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

### Execution Method

   1. **Restore the Database**:  
      Restore the IMBANK database to PostgreSQL and update the `db.py` file with your personal database information.
   
   2. **Install Dependencies**:  
      Install the required modules and libraries by running the following command:  
      ```bash
      pip install -r requirements.txt
      ```
   
   3. **Run the Project**:  
      Start the project by running the following command:  
      ```bash
      python app.py
      ```
   
   4. **Access the Application**:  
      Once the application is running, open your browser (Google Chrome, Safari, or any other browser) and navigate to the local address:  
      ```
      http://127.0.0.1:port
      ```  
      This will allow you to view and interact with the project locally.
