from enum import Enum
from Lexer import Token, TokenType

token = Token(TokenType.INTEGER_CONST, 11)
print(token.type.value)
