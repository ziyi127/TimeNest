"""
自定义异常类
定义业务逻辑层的统一异常层次结构
"""

class TimeNestException(Exception):
    """TimeNest基础异常类"""
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ValidationException(TimeNestException):
    """数据验证异常"""
    def __init__(self, message: str, errors: list = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.errors = errors or []


class ConflictException(TimeNestException):
    """资源冲突异常"""
    def __init__(self, message: str, conflicts: list = None):
        super().__init__(message, "CONFLICT_ERROR")
        self.conflicts = conflicts or []


class NotFoundException(TimeNestException):
    """资源未找到异常"""
    def __init__(self, message: str, resource_id: str = None):
        super().__init__(message, "NOT_FOUND_ERROR")
        self.resource_id = resource_id


class DataAccessException(TimeNestException):
    """数据访问异常"""
    def __init__(self, message: str):
        super().__init__(message, "DATA_ACCESS_ERROR")


class BusinessLogicException(TimeNestException):
    """业务逻辑异常"""
    def __init__(self, message: str):
        super().__init__(message, "BUSINESS_LOGIC_ERROR")