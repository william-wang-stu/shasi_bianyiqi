from enum import Enum
from Error_Detection import LexerError

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
    LG            = '>'
    LT            = '<'

    LTE           = '<='
    NOT_EQUAL     = '!='
    LGE           = '>='
    EQUAL         = '=='

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
        '''
        String representation of the class instance.

        Example:
            Input-token:   Token(TokenType.INTEGER, 7, lineno=5, column=10)
            Output-format: Token(TokenType.INTEGER, 7, position=5:10)
        '''
        return 'Token({type}, {value}, position={lineno}:{column})'.format(
            type=self.type,
            value=repr(self.value),
            lineno=self.lineno,
            column=self.column,
        )

    def __repr__(self):
        return self.__str__()

def _build_reserved_keywords():
    '''
    function: keep all reserved-keywords
    Result:
        {
            'INT': <TokenType.INT: 'INT'>,
            'VOID': <TokenType.VOID: 'VOID'>,
            'IF': <TokenType.IF: 'IF'>,
            'ELSE': <TokenType.ELSE: 'ELSE'>,
            'WHILE': <TokenType.WHILE: 'WHILE'>,
            'RETURN': <TokenType.RETURN: 'RETURN'>
        }
    '''
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
        # input string
        self.text = text
        # index to self.text
        self.pos = 0
        self.current_char = self.text[self.pos]
        # token line number and column number
        self.lineno = 1
        self.column = 1
        # log errors used in UI
        self.err_list = []
    
    def getErrList(self):
        return self.err_list

    def get_all_tokens(self):
        '''
        return a tuple <isEOF, token-list>
            isEOF: true if there is no lexer error,
            and we traverse to the end of the procedure

            token-list: a list of tokens corresponding to the procedure
        '''
        token_list = []
        token = self.get_next_token()
        token_list.append(token)
        flag = True
        while token.type != TokenType.EOF:
            token = self.get_next_token()
            token_list.append(token)
            if token.type == None:
                flag = False
        return (flag, token_list)

    def error(self):
        s = "Lexer error on '{lexeme}' line: {lineno} column: {column}".format(
            lexeme=self.current_char,
            lineno=self.lineno,
            column=self.column,
        )
        # raise LexerError(message=s)
        lexerErr = LexerError(message=s)
        # self.err_list.append(lexerErr)
        self.err_list.append(s)

    def advance(self):
        '''Advance `pos` pointer and set `current_char`'''
        if self.current_char == '\n':
            self.lineno += 1
            self.column = 0

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # end of input
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
        pass

    def number(self):
        '''
        return integer or real number
        number: (digit)+
        digit:  self.current_char.isdigit()
        '''

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
        '''Handle identifiers and reserved keywords'''

        # Create a new token with current line and column number
        token = Token(type=None, value=None, lineno=self.lineno, column=self.column)

        value = ''
        # identifier only includes alpha and num
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
        '''
        function: break self.text into different tokens, and fetch one token once at a time
        '''
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            '''
            pre-process comment in self.text
                self.comment()
            '''

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            # double-character operation token
            if self.current_char == "<" or self.current_char == ">" or self.current_char == "!" or self.current_char == "=":
                if self.peek() == '=':
                    '''
                    LTE           = '<='
                    NOT_EQUAL     = '!='
                    LGE           = '>='
                    EQUAL         = '=='
                    '''
                    # get the whole operation mark
                    double_char_operation = self.current_char + self.peek()
                    # find it!
                    token_type = TokenType(double_char_operation)
                    token = Token(
                        type=token_type,
                        value=token_type.value,  
                        lineno=self.lineno,
                        column=self.column,
                    )
                    # do a double advance
                    self.advance()
                    self.advance()
                    return token


            # single-character token
            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                token_type = TokenType(self.current_char)
            except ValueError as e:
                self.err_list.append(e)
                # no enum member with value equal to self.current_char
                self.error()
                # return None Token
                self.advance()
                return Token(
                    type=None,
                    value=None,
                    lineno=self.lineno,
                    column=self.column,
                )
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
