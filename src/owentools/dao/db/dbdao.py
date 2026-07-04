from __future__ import annotations

from abc import ABC, abstractmethod

import os
import psycopg2
import logging



from owentools.utils.exceptions import UnexpectedException, DatabaseConnectionError
      

class DBDAO(ABC):
  """Base DAO Class for Postgres Tables"""

  def __init__(self, table_name: str, table_query: str):
    # read parameters provided by docker compose environment variables
    self.host = os.getenv("DB_HOST", "db")
    self.database = os.getenv("DB_NAME", "postgres")
    self.user = os.getenv("DB_USER", "postgres")
    self.password = os.getenv("DB_PASSWORD", "secret")
    self.table_name = table_name
    self._ensure_table_exists(table_query)

  def _get_connection(self):
    """
    Raises:
      - DatabaseConnectionError
    """
    try:
      return psycopg2.connect(
        host=self.host,
        database=self.database,
        user=self.user,
        password=self.password,
      )
    except psycopg2.OperationalError as err:
      logging.error(f"Failed to establish live connection database: {err}")
      raise DatabaseConnectionError("Database backend service is unreachable")

  def _ensure_table_exists(self, table_query: str):
    """Initializes database schema structurally if missing
    
    Raises:
      - UnexpectedException
      - DatabaseConnectionError
    """
    connection = None
    cursor = None

    try:
        connection = self._get_connection()
        cursor = connection.cursor()
        cursor.execute(table_query)
        connection.commit()
        logging.info(f"Schema integrity verified: {self.table_name} table exists")
    except Exception as err:
      logging.critical(f"Failed to boostrap application table schema: {err}")
      raise UnexpectedException(err)
    finally:
      if cursor: cursor.close()
      if connection: connection.close()




