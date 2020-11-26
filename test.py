'''
from enum import Enum

class TestEnum(Enum):
    apple = 'this is an apple'
    banana = 'this is a banana'

try:
    s = TestEnum('a')
except ValueError as e:
    print(e)
else:
    print(s)

print("hello world")
'''

from Lexer import Lexer, TokenType
text = '''
void main(void)
{
    %
}
'''
lexer = Lexer(text)

token = lexer.get_next_token()

while token.type != TokenType.EOF and token.type != None:
    token = lexer.get_next_token()
    print (token)

print (lexer.err_list)


from Error_Detection import LexerError

lexerr = LexerError(message="test_message")
lexlist = []
lexlist.append(lexerr)
print(lexerr)
