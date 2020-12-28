### 扩展功能一: 报错
from enum import Enum

class ErrorCode(Enum):
    UNEXPECTED_TOKEN = 'Unexpected token'
    ID_NOT_FOUND     = 'Identifier not found'
    DUPLICATE_ID     = 'Duplicate id found'
    PROCALL_WRONG_TYPE     = 'The type is wrong'
    PARAM_NUM_NOT_SAME     = 'Param num is not the same'
    WRONG_TYPE     = 'The type is wrong'


class Error(Exception):
    def __init__(self, error_code=None, token=None, message=None):
        self.error_code = error_code
        self.token = token
        # add exception class name before the message
        self.message = f'{self.__class__.__name__}: {message}'
    def __str__(self):
        return self.message

class LexerError(Error):
    pass

class ParserError(Error):
    pass

class SemanticError(Error):
    pass
