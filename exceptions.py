class AIServiceError(Exception):
    pass
class AIServiceTimeoutError(AIServiceError):
    pass
class AIServiceConnectionError(AIServiceError):
    pass
class ToolExecutionError(Exception):
    pass