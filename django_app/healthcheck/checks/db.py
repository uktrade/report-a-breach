import asyncio

from django.db import DatabaseError, connection


async def db_check() -> bool:
    """
    Performs a basic check on the database
    """

    def _check():
        try:
            connection.ensure_connection()
            return True
        except DatabaseError:
            return False

    return await asyncio.get_running_loop().run_in_executor(None, _check)
