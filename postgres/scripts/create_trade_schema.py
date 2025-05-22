import psycopg2
import os
import sys
import logging

# --- Configuration ---
DB_HOST = os.getenv('DB_HOST', 'localhost')  # Use 'localhost' if port is mapped, or Docker service name
DB_NAME = os.getenv('DB_NAME', 'tradedb') # Replace with your database name (e.g., 'mydb')
DB_USER = os.getenv('DB_USER', 'jacobg')    # Replace with your PostgreSQL username (e.g., 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Odessa#25') # Replace with your PostgreSQL password
DB_PORT = os.getenv('DB_PORT', '5432') # Default PostgreSQL port, ensure it's mapped from Docker

SQL_SCRIPTS_DIR = '/Users/jacobg/projects/postgres/ddl/tables' # Directory where your SQL files are located

# List SQL files in the order they should be executed.
# This is important for foreign key dependencies (e.g., create Stocks before TradeExecutions).
# If you have one large file, just list that one.
SQL_FILES_TO_EXECUTE = [
    'stocks.sql',
    'brockers.sql',
    'accounts.sql',
    'trade_executions.sql'
   # '01_create_trade_schema.sql', # Assuming you put all table creation SQL here
    # Add more if you split your schema into multiple files (e.g., '02_create_indexes.sql')
]

# --- Logging Setup ---
# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO, # Set this to logging.DEBUG for more verbose output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # Output to console
        # You could add logging.FileHandler('schema_creation.log') for file output
    ]
)
logger = logging.getLogger(__name__)

# --- Main Script ---

def create_schema():
    """
    Connects to the PostgreSQL database and executes SQL scripts
    to create the schema.
    """
    conn = None
    try:
     #   print(f"Attempting to connect to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}...")
        logger.info(f"Attempting to connect to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        conn.autocommit = True # Set to True to commit each statement, or manage transactions manually
        cur = conn.cursor()
        logger.info("Successfully connected to the database.")

        for sql_file_name in SQL_FILES_TO_EXECUTE:
            sql_file_path = os.path.join(SQL_SCRIPTS_DIR, sql_file_name)
            if not os.path.exists(sql_file_path):
                logger.info(f"Error: SQL file not found: {sql_file_path}", file=sys.stderr)
                continue

            logger.info(f"Executing SQL script: {sql_file_name}...")
            with open(sql_file_path, 'r') as f:
                sql_script = f.read()

            try:
                # Execute the script. psycopg2's execute method handles multiple statements
                # when `autocommit` is True, or if the script is a single large statement.
                # For complex scripts with transactions, you might parse them into individual
                # statements or use a library like sqlparse.
                cur.execute(sql_script)
                logger.info(f"Successfully executed {sql_file_name}.")
            except psycopg2.Error as e:
                logger.info(f"Error executing {sql_file_name}: {e}", file=sys.stderr)
                # It's often good to stop on the first error for schema creation
                sys.exit(1) # Exit with an error code

    except psycopg2.Error as e:
        logger.info(f"Database connection or query error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            cur.close()
            conn.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    create_schema()
