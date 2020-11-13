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
    
    def program(self):
        '''program : type_spec variable LPAREN formal_param_list RPAREN block'''
        program_type = self.type_spec()
        program_name = self.variable().value
        self.eat(TokenType.LPAREN)
        program_param = self.formal_param_list()
        self.eat(TokenType.RPAREN)
        program_block = self.block()
        # program_node = Program()
        # return program_node
    
    def type_spec(self):
        '''type_spec : INT | VOID'''
        token = self.current_token
        if self.current_token.type == TokenType.INT:
            self.eat(TokenType.INT)
        else:
            self.eat(TokenType.VOID)
        # type_node = Type()
        # return type_node

    def formal_param_list(self):
        '''formal_param_list : formal_param | VOID | EMPTY'''
        if self.current_token.type == TokenType.INT:
            param_list = self.formal_param()
        elif self.current_token.type == TokenType.VOID:
            param_list = [TokenType.VOID]
            self.eat(TokenType.VOID)
        else:
            param_list = []
        
        return param_list
    
    def formal_param(self):
        '''formal_param : INT ID ( COMMA INT ID )*'''
        param_list = []

        self.eat(TokenType.INT)
        param_list.append(self.current_token)
        self.eat(TokenType.ID)
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            param_list.append(self.current_token)
            self.eat(TokenType.ID)
        
        return param_list
    
    def block(self):
        '''block : LBRACE declarations compound_statement RBRACE'''
        self.eat(TokenType.LBRACE)
        declarations = self.declarations()
        compound_statement = self.compound_statement()
        self.eat(TokenType.RBRACE)
        # block_node = Block()
        # return block_node

    def declarations(self):
        '''declarations : empty | ( variable_declaration SEMI )*'''
        declaration_list = []

        while self.current_token.type == TokenType.INT:
            variable_declaration = self.variable_declaration()
            declaration_list.append(variable_declaration)
            self.eat(TokenType.SEMI)
        
        return declaration_list

    def empty(self):
        pass

    def variable_declaration(self):
        '''variable_declaration : INT ID'''
        self.eat(TokenType.INT)
        var_name = self.variable()
        var_type = TokenType.INTEGER_CONST
        # var_node = VarNode()
        # retunr var_node
    
    def compound_statement(self):
        '''compound_statement : ( statement )+'''
        statement_list = []

        while self.current_token.type == TokenType.ID or self.current_token.type == TokenType.RETURN or self.current_token.type == TokenType.IF or self.current_token.type == TokenType.WHILE:
            statement = self.statement()
            statement_list.append(statement)
        
        return statement_list

    def statement(self):
        '''statement : assignment_statement | return_statement | while_statement | if_statement'''
        if self.current_token.type == TokenType.ID:
            statement = self.assignment_statement()
        elif self.current_token.type == TokenType.RETURN:
            statement = self.return_statement()
        elif self.current_token.type == TokenType.IF:
            statement = self.if_statement()
        else:
            statement = self.while_statement()
        
        return statement

    def assignment_statement(self):
        '''assignment_statement : ID ASSIGN expr SEMI'''
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASSIGN)
        right = self.expr()
        self.eat(TokenType.SEMI)
    
    def return_statement(self):
        '''return_statement : RETURN ( expr )? SEMI'''
        self.eat(TokenType.RETURN)

        if self.current_token.type != TokenType.SEMI:
            node = self.expr()
        
        self.eat(TokenType.SEMI)
    
    def while_statement(self):
        '''while_statement : WHILE LPAREN expr RPAREN block'''
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        expr = self.expr()
        self.eat(TokenType.RPAREN)
        block = self.block()
    
    def if_statement(self):
        '''if_statement : IF LPAREN expr RPAREN block ( ELSE block )?'''
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        self.eat(TokenType.RPAREN)
    
    def parse(self):
        '''
        program                 : type_spec variable LPAREN formal_param_list RPAREN block

        type_spec               : INT | VOID

        formal_param_list       : formal_param | VOID | EMPTY

        formal_param            : INT ID ( COMMMA INT ID )*

        block                   : LBRACE declarations compound_statement RBRACE

        declarations            : empty | ( variable_declaration SEMI )*

        empty : 

        variable_declaration    : INT ID

        compound_statement      : ( statement )+

        statement               : assignment_statement | return_statement | while_statement | if_statement

        assignment_statement    : ID ASSIGN expr SEMI

        return_statement        : RETURN ( expr )? SEMI

        while_statement         : WHILE LPAREN expr RPAREN block

        if_statement            : IF LPAREN expr RPAREN block ( ELSE block )?

        expr                    : relop_term ( relop relop_term )*

        relop                   : LT | LTE | LG | LGE | EQUAL | NOT_EQUAL

        relop_term              : term ( (PLUS | MINUS) term )*

        term                    : factor ( (MUL | DIV) factor )*

        factor                  : INTEGER_CONST | LPAREN expr RPAREN | ID | ID LPAREN actual_param RPAREN

        actual_param            : expr (COMMA expr)*
        
        variable                : ID

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

