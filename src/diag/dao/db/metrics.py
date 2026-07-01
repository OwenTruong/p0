from __future__ import annotations
import psycopg2
import logging
from datetime import datetime
from typing import ClassVar, List


from diag.utils.exceptions import DatabaseConnectionError, UnexpectedException

from diag.data.systems import CPU, Memory, Storage, Systems, UnixSocketState
from diag.data.metrics import Metrics
from diag.dao.linux.systems import SystemsDAO

from diag.dao.db.dbdao import DBDAO


class MetricsDAO(DBDAO):
  def __init__(self):
    table_name = "metrics"
    table_query = """
      CREATE TABLE IF NOT EXISTS metrics (
        id SERIAL PRIMARY KEY,
        cpu_logical_core_count INT NOT NULL,
        cpu_average DOUBLE PRECISION NOT NULL,
        memory_total BIGINT NOT NULL,
        memory_used BIGINT NOT NULL,
        created_on TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
      );
    """
    super().__init__(table_name, table_query)

  def create(self, cpu_logical_core_count: int, cpu_average: float, memory_total: int, memory_used: int):
    connection = None
    try:
        connection = self._get_connection()
        with connection.cursor() as cursor:
          query = "INSERT INTO metrics (cpu_logical_core_count, cpu_average, memory_total, memory_used) VALUES(%s, %s, %s, %s) RETURNING *;" 
          cursor.execute(query, (cpu_logical_core_count, cpu_average, memory_total, memory_used))
          row = cursor.fetchone()
          if row is None:
            raise UnexpectedException("Fetched row is None after insertion")
          connection.commit()
          logging.info(f"Successfully recorded metric entry")
          metrics = Metrics(
            id=row[0],
            cpu_logical_core_count=row[1],
            cpu_average=row[2],
            memory_total=row[3],
            memory_used=row[4],
            created_on=row[5]
          )
          return metrics
    except DatabaseConnectionError:
      raise
    except Exception as err:
      logging.error(f"Failed to create new record: {err}")
      raise UnexpectedException()
    finally:
      if connection: connection.close()
  
  def read_all(self) -> List[Metrics]:
    connection = None
    try:
      connection = self._get_connection()
      with connection.cursor() as cursor:
        query = "SELECT * FROM metrics ORDER BY created_on;"
        cursor.execute(query)
        rows = cursor.fetchall()
        metrics_li = []

        for row in rows:
          metrics = Metrics(
            id=row[0],
            cpu_logical_core_count=row[1],
            cpu_average=row[2],
            memory_total=row[3],
            memory_used=row[4],
            created_on=row[5]
          )
          metrics_li.append(metrics)
        return metrics_li
    except DatabaseConnectionError:
      raise
    except Exception as err:
      logging.error(f"Failed to read a record: {err}")
      raise UnexpectedException()
    finally:
      if connection: connection.close()

  def delete_by_id(self, id: int):
    connection = None
    try:
        connection = self._get_connection()
        with connection.cursor() as cursor:
          query = "DELETE FROM metrics WHERE id = %s"
          cursor.execute(query, (id,))
          logging.info(f"Successfully deleted metrics")
          connection.commit()
          pass
    except DatabaseConnectionError:
      raise
    except Exception as err:
      logging.error(f"Failed to delete a record: {err}")
      raise UnexpectedException()
    finally:
      if connection: connection.close()