from enum import Enum

### todo
# 注释:
#   功能: 需要修改成 // 和 /**/
#   位置: 232行的 if-else 块
#         167行的 skip_comment()
# 两个单词组成的字符判断:
#   功能: 现在所有的词法分析都是用昨天说的那个trick来识别单个字符,
#         所以对于其他字符(比如: >=), 需要使用peek()来修改if-else块
#         另外, 249行的赋值号也需要修改(原来是:=, 要求是=)
# 测试:
#   功能: 现在main函数部分是用来作测试的, 被注释部分是正式版本;
#         现在需要增加更多的测试, 最基本的是把上述两个功能完成以后, 跑一下PPT里的大作业部分看下行不行

### 扩展功能一: 报错
class Error(Exception):
    def __init__(self, error_code=None, token=None, message=None):
        self.error_code = error_code
        self.token = token
        # add exception class name before the message
        self.message = f'{self.__class__.__name__}: {message}'

class LexerError(Error):
    pass


### 词法分析器
class TokenType(Enum):
    # 关键字 - RESERVED KEYWORDS
    INT = 'INT'
    VOID = 'VOID'
    IF = 'IF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    RETURN = 'RETURN'

    # 标识符
    ID = 'ID'
    
    # 数值
    INTEGER_CONST = 'INTEGER_CONST'
    REAL_CONST = 'REAL_CONST'

    # 赋值号
    ASSIGN = '='

    # 算符
    PLUS          = '+'
    MINUS         = '-'
    MUL           = '*'
    DIV           = '/'
    EQUAL         = '=='
    LG            = '>'
    LGE           = '>='
    LT            = '<'
    LTE           = '<='
    NOT_EQUAL     = '!='

    # 界符
    SEMI          = ';'

    # 分隔符
    COMMA         = ','

    # 注释号


    # 左/右括号
    LPAREN        = '('
    RPAREN        = ')'

    # 左/右大括号
    LBRACE        = '{'
    RBRACE        = '}'

    EOF           = '#'

class Token:
    def __init__(self, type, value, lineno=None, column=None):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.column = column

    def __str__(self):
        """
        String representation of the class instance.

        Example:
            Input-token:   Token(TokenType.INTEGER, 7, lineno=5, column=10)
            Output-format: Token(TokenType.INTEGER, 7, position=5:10)
        """
        return 'Token({type}, {value}, position={lineno}:{column})'.format(
            type=self.type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column,
        )

    def __repr__(self):
        return self.__str__()

def _build_reserved_keywords():
    """
    关键字字典: TokenType中的所有关键字部分, 从INT开始, 到RETURN结束

    Result:
        {'PROGRAM': <TokenType.PROGRAM: 'PROGRAM'>,
         'INTEGER': <TokenType.INTEGER: 'INTEGER'>,
         'REAL': <TokenType.REAL: 'REAL'>,
         'DIV': <TokenType.INTEGER_DIV: 'DIV'>,
         'VAR': <TokenType.VAR: 'VAR'>,
         'PROCEDURE': <TokenType.PROCEDURE: 'PROCEDURE'>,
         'BEGIN': <TokenType.BEGIN: 'BEGIN'>,
         'END': <TokenType.END: 'END'>}
    """
    # enumerations support iteration, in definition order
    tokentype_list = list(TokenType)
    start_index = tokentype_list.index(TokenType.INT)
    end_index = tokentype_list.index(TokenType.RETURN)
    reserved_keywords = {
        token_type.value: token_type
        for token_type in tokentype_list[start_index:end_index + 1]
    }
    return reserved_keywords

RESERVED_KEYWORDS = _build_reserved_keywords()

class Lexer:
    def __init__(self, text):
        # client string input"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]
        # token line number and column number
        self.lineno = 1
        self.column = 1

    def error(self):
        s = "Lexer error on '{lexeme}' line: {lineno} column: {column}".format(
            lexeme=self.current_char,
            lineno=self.lineno,
            column=self.column,
        )
        raise LexerError(message=s)

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        if self.current_char == '\n':
            self.lineno += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]
            self.column += 1

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char != '}':
            self.advance()
        self.advance()  # the closing curly brace

    def number(self):
        """Return a (multidigit) integer or float consumed from the input."""

        # Create a new token with current line and column number
        token = Token(type=None, value=None, lineno=self.lineno, column=self.column)

        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == '.':
            result += self.current_char
            self.advance()

            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

            token.type = TokenType.REAL_CONST
            token.value = float(result)
        else:
            token.type = TokenType.INTEGER_CONST
            token.value = int(result)

        return token

    def _id(self):
        """Handle identifiers and reserved keywords"""

        # Create a new token with current line and column number
        token = Token(type=None, value=None, lineno=self.lineno, column=self.column)

        value = ''
        while self.current_char is not None and self.current_char.isalnum():
            value += self.current_char
            self.advance()

        token_type = RESERVED_KEYWORDS.get(value.upper())
        if token_type is None:
            token.type = TokenType.ID
            token.value = value
        else:
            # reserved keyword
            token.type = token_type
            token.value = value.upper()

        return token

    def get_next_token(self):
        """
        Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            '''
            if self.current_char == '{':
                self.advance()
                self.skip_comment()
                continue
            '''

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == ':' and self.peek() == '=':
                token = Token(
                    type=TokenType.ASSIGN,
                    value=TokenType.ASSIGN.value,  # ':='
                    lineno=self.lineno,
                    column=self.column,
                )
                self.advance()
                self.advance()
                return token

            # single-character token
            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                token_type = TokenType(self.current_char)
            except ValueError:
                # no enum member with value equal to self.current_char
                self.error()
            else:
                # create a token with a single-character lexeme as its value
                token = Token(
                    type=token_type,
                    value=token_type.value,  # e.g. ';', '.', etc
                    lineno=self.lineno,
                    column=self.column,
                )
                self.advance()
                return token

        # EOF (end-of-file) token indicates that there is no more
        # input left for lexical analysis
        return Token(type=TokenType.EOF, value=None)

class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()
    
    def eat(self):
        self.current_token = self.lexer.get_next_token()

example_text_list = [
    # '24abc',
    # '24abc\n123',
    # '(abc){123}',
    # 'if123',
    # 'if=123',
    '''
int  program(int a,int b,int c)
{
	int i;
	int j;
	i=0; 	
	if(a>(b+c))
	{
		j=a+(b*c+1);
	}
	else
	{
		j=a;
	}
	while(i<100)
	{
		i=j*2;
	}
	return i;
}
'''
]

if __name__ == '__main__':
    for example_text in example_text_list:
        print(f"Lexer for {example_text}:")
        lexer = Lexer(example_text)
        while True:
            token = lexer.get_next_token()
            if token.type == TokenType.EOF:
                break
            print(token)
    
    '''
    while True:
        try:
            text = input('Lexer> ')
        except EOFError:
            break
        if not text:
            continue

        lexer = Lexer(text)
        while True:
            token = lexer.get_next_token()
            if token.type == TokenType.EOF:
                break
            print(token)
    '''
    