from flask import Flask, Blueprint, render_template
from user import user_bp  # Import the user blueprint
from admin import admin_bp  # Import the admin blueprint
from bank import bank_bp  # Import the bank blueprint
from card import card_bp  # Import the card blueprint
from db import get_db_connection
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(bank_bp, url_prefix='/bank')
app.register_blueprint(card_bp, url_prefix='/card')

# Set the secret key and session configurations
app.secret_key = 'your_secret_key'
app.config.update(
    SESSION_COOKIE_NAME='session',
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30)
)

# Flag to ensure create_indexes is called only once
initialization_done = False

# Function to create database indexes
def create_indexes():
    """
    Creates database indexes for optimizing queries. 
    This function should only be called during database setup or maintenance.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create index on bankerid in the branch table, if it doesn't already exist
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_branch_bankerid 
            ON branch(bankerid);
        """)

        # Create index on branchid in the branch table, if it doesn't already exist
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_branch_branchid 
            ON branch(branchid);
        """)

        # Create index on day in the openinghour table, if it doesn't already exist
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_openinghour_day 
            ON openinghour(day);
        """)

        # Optional: Create composite index on bankerid and branchid in the branch table, if it doesn't already exist
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_branch_bankerid_branchid 
            ON branch(bankerid, branchid);
        """)

        # Optional: Create composite index on branchid and day in the openinghour table, if it doesn't already exist
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_openinghour_branchid_day 
            ON openinghour(branchid, day);
        """)
   

        # Commit the changes to the database
        conn.commit()
        print("indexes have been sucessfully created")
    
    except Exception as e:
        conn.rollback()
        print(f"An error occurred while creating indexes: {e}")
    
    finally:
        cur.close()
        conn.close()

# Initialize indexes before any request
@app.before_request
def initialize_indexes():
    global initialization_done
    if not initialization_done:
        print("Initializing database indexes...")
        create_indexes()
        initialization_done = True

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True, port=5678)
