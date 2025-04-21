import os

def get_db_config():
    """Return DB config dictionary from environment variables."""
    return {
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
    }

def get_coins_table():
    """Return the coins table name from environment variables (default: 'coins')."""
    return os.getenv('POSTGRES_TABLE', 'coins')
