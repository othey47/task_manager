# Import sqlite3 to work with an SQLite database.
import sqlite3


# Define a function responsible for creating and returning a database connection.
def get_db_connection():

    # Connect to the SQLite database file named tasks.db.
    # If the file doesn't exist, SQLite will create it automatically.
    connect = sqlite3.connect("tasks.db")

    # Configure the connection to return database rows as dictionary-like objects.
    # This allows us to access column values using their names,
    # for example: row['title'] instead of row[1].
    connect.row_factory = sqlite3.Row

    # Return the database connection so other functions can use it.
    return connect


# Define a function responsible for initializing the database.
def init_db():

    # Get a connection to the SQLite database.
    connect = get_db_connection()

    # Create the table and define its columns.    
    connect.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            due_date TEXT
        )
    """)

    # Save the database changes.
    connect.commit()

    # Close the database connection to release resources.
    connect.close()
