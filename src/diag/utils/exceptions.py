class UnexpectedException(Exception):
  """Raised when an excpetion happens due to some bug or unexpected variable on the application's side."""
  pass

class DatabaseConnectionError(Exception):
  """Raised when the application cannot reach the PostgreSQL Database Instance."""
  pass

class MetricCreationError(Exception):
  """Raised when an insertion operation violates constraints or fails."""
  pass

class SingletonNotInitializedError(Exception):
  """Raised when attempting to retrieve a singleton when it has not been initalized yet"""