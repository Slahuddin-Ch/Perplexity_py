import os
import bcrypt
import json
from _sqlite3 import *
from sqlalchemy import Table, Column, Integer, Text, Enum, JSON, MetaData, create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Base directory for user-specific databases and user credentials
BASE_DB_DIR = "database/user_databases"
CREDENTIALS_FILE = "database/credentials.json"

# Metadata object for defining tables
metadata = MetaData()

# Messages table
messages = Table(
    'messages',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('content', Text, nullable=False),
    Column('chatId', Text, nullable=False),
    Column('messageId', Text, nullable=False),
    Column('role', Enum('assistant', 'user', name='role_type')),
    Column('metadata', JSON),
)

# Chats table
chats = Table(
    'chats',
    metadata,
    Column('id', Text, primary_key=True),
    Column('title', Text, nullable=False),
    Column('createdAt', Text, nullable=False),
    Column('focusMode', Text, nullable=False),
)


def get_user_session(user_id):
    """
    Get a database session dynamically for a specific user ID.
    """
    # Ensure base directory exists
    os.makedirs(BASE_DB_DIR, exist_ok=True)

    # Dynamic path for the user's SQLite database
    db_path = os.path.join(BASE_DB_DIR, f"{user_id}.db")
    db_url = f"sqlite:///{db_path}"

    # Create engine and session for this user's database
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    # Ensure tables are created if not already
    metadata.create_all(engine)

    return Session()


def add_message(user_id, chat_id, message_id, content, role, metadata=None):
    """
    Add a message to the user's chat history.
    """
    session = get_user_session(user_id)
    try:
        session.execute(
            messages.insert().values(
                chatId=chat_id,
                messageId=message_id,
                content=content,
                role=role,
                metadata=metadata,
            )
        )
        session.commit()
    except IntegrityError as e:
        session.rollback()
        print(f"Error adding message for user {user_id}: {e}")
    finally:
        session.close()


def get_chat_history(user_id, chat_id):
    """
    Fetch chat history for a specific user and chat ID.
    """
    session = get_user_session(user_id)
    try:
        query = select(messages).where(messages.c.chatId == chat_id).order_by(messages.c.id)
        result = session.execute(query).fetchall()
        return result
    except Exception as e:
        print(f"Error fetching chat history for user {user_id} and chat ID {chat_id}: {e}")
        return []
    finally:
        session.close()


def get_all_chat_ids(user_id):
    """
    Fetch all chat IDs for the user.
    """
    session = get_user_session(user_id)
    try:
        query = select(messages.c.chatId).distinct()
        result = session.execute(query).fetchall()
        # Extract chat IDs from the result
        return [row[0] for row in result]
    except Exception as e:
        print(f"Error fetching all chat IDs for user {user_id}: {e}")
        return []
    finally:
        session.close()


def delete_chat_history(user_id, chat_id):
    """
    Delete chat history for a specific user and chat ID.
    """
    session = get_user_session(user_id)
    try:
        session.execute(messages.delete().where(messages.c.chatId == chat_id))
        session.commit()
        print(f"Chat history for chat ID {chat_id} deleted successfully.")
    except IntegrityError as e:
        session.rollback()
        print(f"Error deleting chat history for user {user_id} and chat ID {chat_id}: {e}")
    finally:
        session.close()


def load_credentials():
    """Load stored user credentials from a JSON file."""
    if not os.path.exists(CREDENTIALS_FILE):
        return {}
    with open(CREDENTIALS_FILE, "r") as file:
        return json.load(file)


def save_credentials(credentials):
    """Save user credentials to a JSON file."""
    os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
    with open(CREDENTIALS_FILE, "w") as file:
        json.dump(credentials, file)


def authenticate_user():
    """
    Authenticate the user or create a new account with unique usernames.
    """
    os.makedirs(BASE_DB_DIR, exist_ok=True)  # Ensure the base directory exists
    credentials = load_credentials()

    while True:
        print("\nWelcome! Please log in or create a new account.")
        username = input("Enter your username: ").strip()
        if not username:
            print("Username cannot be empty. Please try again.")
            continue

        if username in credentials:
            # Authenticate existing user
            print(f"Username '{username}' found. Please log in.")
            password = input("Enter your password: ").strip()

            # Validate password
            stored_password_hash = credentials[username]
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                print(f"Welcome back, {username}!")
                return username
            else:
                print("Incorrect password. Please try again.")
                continue
        else:
            # Create a new user
            print(f"Username '{username}' not found. Creating a new account...")
            password = input("Enter your password: ").strip()
            if not password:
                print("Password cannot be empty. Please try again.")
                continue

            # Hash and store the password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            credentials[username] = password_hash
            save_credentials(credentials)

            # Initialize user database
            initialize_user_database(username)
            print(f"Account created for {username}. Please proceed.")
            return username


def initialize_user_database(user_id):
    """
    Initialize a database for a new user if it doesn't exist.
    """
    user_db_path = os.path.join(BASE_DB_DIR, f"{user_id}.db")
    if not os.path.exists(user_db_path):
        print(f"Initializing database for user {user_id}...")
        get_user_session(user_id)  # This will create the database and tables
    else:
        print(f"Database for user {user_id} already exists.")
