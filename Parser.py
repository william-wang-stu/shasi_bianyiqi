from Error_Detection import ParserError, ErrorCode
from Lexer import TokenType


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.get_next_token()

    def get_next_token(self):
        return self.lexer.get_next_token()

    def error(self, error_code, token):
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )

    def parse(self):
        '''
        Program : Type Variable LPAREN RPAREN Block

        Type    : INT | VOID

        Block   : LBRACE Declarations Compound_statement RBRACE

        Declarations            : Empty | Variable_declaration ( SEMI Variable_declaration )*

        Empty   : 

        Variable_declaration    : INT Variable

        Compound_statement      : (Statement)+

        Statement   : Assignment_statement | Return_statement | While_statement | If_statement

        Assignment_statement    : Variable ASSIGN Expr

        Return_statement        : RETURN ( Expr )*

        While_statement         : WHILE LPAREN Expr RPAREN Block

        If_statement            : IF LPAREN Expr RPAREN Block ( ELSE Block )*

        Expr        : Relop_term ( Relop Relop_term )*

        Relop       : LT | LTE | LG | LGE | EQUAL | NOT_EQUAL

        Relop_term  : Term ( (PLUS | MINUS) Term )*

        Term        : Factor ( (MUL | DIV) Factor )*

        Factor      : INTEGER_CONST | LPAREN Expr RPAREN | Variable Formal_parameters

        Formal_parameters       : Empty | Proccall_statement
        
        Proccall_statement      : LPAREN Expr (COMMA Expr)* RPAREN

        Variable    : ID
        
        '''
        node = self.program()
        if self.current_token.type != TokenType.EOF:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )

        return node
    
    def parse_proccall(self):
        '''
        Program : Declaration_list

        Declaration_list : ( Proc_declaration )*

        Proc_declaration : INT Variable Type_declaration | VOID Variable Func_decaration

        Type_declaration : Var_declaration | Func_declaration

        Var_declaration  : SEMI

        Func_declaration : LPAREN Param_list RPAREN Block

        Param_list       : Param (SEMI Param)*

        Param   : INT Variable

        Block   : LBRACE Declarations Compound_statement RBRACE

        Declarations            : Empty | Variable_declaration ( SEMI Variable_declaration )*

        Empty   : 

        Variable_declaration    : INT Variable

        Compound_statement      : (Statement)+

        Statement   : Assignment_statement | Return_statement | While_statement | If_statement

        Assignment_statement    : Variable ASSIGN Expr

        Return_statement        : RETURN ( Expr )*

        While_statement         : WHILE LPAREN Expr RPAREN Block

        If_statement            : IF LPAREN Expr RPAREN Block ( ELSE Block )*

        Expr        : Relop_term ( Relop Relop_term )*

        Relop       : LT | LTE | LG | LGE | EQUAL | NOT_EQUAL

        Relop_term  : Term ( (PLUS | MINUS) Term )*

        Term        : Factor ( (MUL | DIV) Factor )*

        Factor      : INTEGER_CONST | LPAREN Expr RPAREN | Variable Formal_parameters

        Formal_parameters       : Empty | Proccall_statement
        
        Proccall_statement      : LPAREN Expr (COMMA Expr)* RPAREN

        Variable    : ID
        '''
        node = self.program()
        if self.current_token.type != TokenType.EOF:
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token,
            )

        return node

