class AIServiceError(Exception):
    pass
class AIServiceTimeoutError(AIServiceError):
    pass
class AIServiceConnectionError(AIServiceError):
    pass