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
# Program Explanation

   1. **Core Files**:
      - **app.py**: The main entry point of the application. Initializes the Flask app, manages HTTP requests, registers blueprints, and ensures database index creation for optimized queries.
      - **db.py**: Handles PostgreSQL database connections and interactions, such as retrieving user accounts and transaction data.
   
   2. **User Functions**:
      - **user.py**: Manages user-specific operations, including account registration, login, balance checks, transaction history, performing transactions, loan applications, loan history searches, and loan repayments.
      - **card.py**: Handles credit card operations such as card registration, transaction history retrieval, and monthly bill repayment.
      - **bank.py**: Provides functionality for customers to search for bank and branch information.
   
   3. **Admin Functions**:
      - **admin.py**: Manages administrative operations, including user account management, loan application approvals or rejections, and access to transaction records.
   
   These files work together to create a complete online banking system, with each part handling a specific aspect of the platform.
# Technical Details

   - **Session Management**: Flask's session handling is secured using a secret key to sign cookies, HTTPS-only cookie transmission, and restricted HTTP-only access. Sessions have a 30-minute lifetime to enhance security and manage user interactions effectively. Each user's session is tied to a unique session ID, ensuring that user logins do not override across different windows or browsers.
   
   - **Blueprints**: Flask Blueprints are used to modularize the application. Separate blueprints handle specific functionalities (e.g., user, admin, bank, and card operations), improving code organization and scalability.
   
   - **Database**: PostgreSQL is used as the database, with Psycopg2 facilitating interactions.
   
   - **Transaction Management**:  
     - If a violation of table constraints occurs during a write operation, the transaction is immediately stopped, and a **ROLLBACK** is executed to undo all changes.  
     - Upon successful completion, a **COMMIT** is issued to ensure all changes are permanently saved.
   
   - **Concurrency Control**:  
     - Multiple locks are implemented to maintain data consistency, particularly during critical operations such as transactions, preventing race conditions and ensuring integrity.
# DEMO Video
# Development Environment

- **Operating System**: macOS  
- **Database**: PostgreSQL 16.4  
- **Programming Language**: Python 3.12.7 (Anaconda)  
  - **Key Library**: psycopg2 2.9.10  






# Execution Method  

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
      Once the application is running, open your browser (e.g., Google Chrome, Safari) and navigate to the following address:  
      ```
      http://127.0.0.1:<port>
      ```  
      Replace `<port>` with the port number your application is running on (e.g., `5678`). If the designated port is occupied, you can change the port number in your Flask configuration and try again.
