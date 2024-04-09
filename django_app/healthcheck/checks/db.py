from django.db import DatabaseError, connection


def db_check() -> bool:
    """
    Performs a basic check on the database
    """
    try:
        connection.ensure_connection()
        return True
    except DatabaseError:
        return False
