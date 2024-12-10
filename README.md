# 113-1 Database Management - I'm Bank



# Overview  
This is the database final project for the NTUIM course. We implemented a bank system called **" I’m Bank "** using PostgreSQL, Flask, and simple HTML. **" I’m Bank "** is a platform that provides various online financial services for both banks and customers. Its primary purpose is to enable customers of different banks to manage their personal bank accounts, access account information, and utilize a range of financial services.

# System Features


The platform supports two user roles: **User** and **Admin**. Users, representing customers, can access key services offered by the bank, including those related to loans, account management, and credit card services. Admins, who represent the bank staff, are responsible for managing loan services, accessing account details, and more.

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


- ## Admin Functions in the System
   
   1. **Import User Information**: Import new user data into the system.
   2. **Manage Accounts**: Filter and view individual account information, including assets and transaction records.
   3. **Manage Loans**: Assess users to decide whether to approve loans and view all loan records.
   4. **Manage Credit Cards**: Approve or deny credit card applications and view all credit card information.
   5. **View Account Transaction History**: View all account transaction records.
   6. **User Data Analysis**: Set conditions to filter users and obtain statistics on user assets, total loan amounts, total repayments, and more.


# Program Explanation

   1. **Core Files**:
      - **app.py**: The main entry point of the application. Initializes the Flask app, manages HTTP requests, registers blueprints, and ensures database index creation for optimized queries.
      - **db.py**: Handles PostgreSQL database connections and interactions, such as retrieving user accounts and transaction data.
   
   2. **User Functions**:
      - **user.py**: Manages user-specific operations, including account registration, login, balance checks, transaction history, performing transactions, loan applications, loan history searches, and loan repayments.
      - **card.py**: Handles credit card operations such as card registration, transaction history retrieval, and monthly bill repayment.
      - **bank.py**: Provides functionality for customers to search for bank and branch information.
   
   3. **Admin Functions**:
      - **admin.py**: Manages admin tasks such as importing user information, handling user accounts, processing loan and credit card applications, reviewing transaction records, and performing user data analysis. These functions are key to overseeing the banking system's operations and generating insights.
   
   These files work together to create a complete online banking system, with each part handling a specific aspect of the platform.
# Technical Details

   - **Session Management**: Flask’s session handling is secured with a secret key to sign cookies, HTTPS-only transmission, and restricted HTTP-only access. Sessions are configured with a 30-minute lifetime for better security and user interaction management. To prevent session data from being overwritten on the same machine, use different browsers (e.g., Chrome and Safari) or one in normal mode and one in incognito mode.
   
   - **Blueprints**: Flask Blueprints are used to modularize the application. Separate blueprints handle specific functionalities (e.g., user, admin, bank, and card operations), improving code organization and scalability.
   
   - **Database**: PostgreSQL is used as the database, with Psycopg2 facilitating interactions.
   
   - **Transaction Management**:  
     - If a violation of table constraints occurs during a write operation, the transaction is immediately stopped, and a **ROLLBACK** is executed to undo all changes.  
     - Upon successful completion, a **COMMIT** is issued to ensure all changes are permanently saved.
   
   - **Concurrency Control**:  
     - Multiple locks are implemented to maintain data consistency, particularly during critical operations such as transactions, preventing race conditions and ensuring integrity.
# DEMO Video
 [![Demo Video](https://img.youtube.com/vi/oKar-tF__ac/0.jpg)](https://www.youtube.com/watch?v=oKar-tF__ac)




# Development Environment:

- **Operating System**: macOS 14.4.1
- **Python Version**: 3.12.7
- **PostgreSQL Version**: PostgreSQL 17.0 (compiled by Apple clang version 16.0.0)
- **Psycopg2 Version**: 2.9.10 (installed via Anaconda, also includes `psycopg2-binary` version 2.9.10)
- **Dependencies**:
  - `psycopg2==2.9.6`
  - `Werkzeug==2.2.3`
  - `Faker==18.6.1`
  - `python-dateutil==2.8.2`
- **IDE**: VS Code, running in an Anaconda environment.






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
      Replace `<port>` with the port number your application is running on (default: `5678`). If the designated port is occupied, you can change the port number in your Flask configuration and try again.

# Reference
The README.md file is based on the "資料庫管理（113-1）期末專案完整報告."

