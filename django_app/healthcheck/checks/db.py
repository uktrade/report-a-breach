import asyncio

from django.db import DatabaseError, connection


async def db_check() -> bool:
    """
    Performs a basic check on the database
    """
    loop = asyncio.get_event_loop()

    def _check():
        try:
            connection.ensure_connection()
            return True
        except DatabaseError:
            return False

    return await loop.run_in_executor(None, _check)
