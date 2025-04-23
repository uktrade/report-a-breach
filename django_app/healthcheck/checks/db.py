from asgiref.sync import sync_to_async
from django.db import DatabaseError, connection


@sync_to_async(thread_sensitive=False)
def testdb_check() -> bool:
    """
    Performs a basic check on the database
    """
    try:
        connection.ensure_connection()
        return True
    except DatabaseError:
        return False
