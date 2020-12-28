from Error_Detection import ParserError, ErrorCode
from Lexer import TokenType, Lexer
from ParserTree import *

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.get_next_token()
        # log errors to be used in UI
        self.err_list = []

    def get_next_token(self):
        return self.lexer.get_next_token()

    def getErrList(self):
        return self.err_list

    def error(self, error_code, token):
        '''
        raise ParserError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )
        '''
        parserErr = ParserError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )
        self.err_list.append(parserErr)

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
        '''
        program : ( type_spec variable SEMI | type_spec variable LPAREN formal_param_list RPAREN block )+
        '''
        '''
        within this grammar-rule, we only include var-declaration
        i.e. int a;
        and func-declaration
        i.e. int func()
        {
        }
        '''
        
        func_list = []

        # restrict return-type to be INT or VOID
        while self.current_token.type in (TokenType.INT, TokenType.VOID):
            type_node = self.type_spec()
            var_node  = self.variable()
            # global var  i.e int a;
            if self.current_token.type == TokenType.SEMI:
                self.eat(TokenType.SEMI)
                node = VarDecl(var_node, type_node)
            # func declaration  i.e int func() { <block> }
            elif self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                # fetch param-list of the function
                program_params = self.formal_param_list()
                self.eat(TokenType.RPAREN)
                program_block = self.block()
                node = Function(
                    type = type_node,
                    name = var_node.value,
                    formal_params = program_params,
                    block = program_block
                )
                # print(node.type)
            else:
                node = NoOp()
                self.error(
                    error_code=ErrorCode.UNEXPECTED_TOKEN,
                    token=self.current_token
                )
            func_list.append(node)

        if not func_list:
            func_list.append(NoOp())

        root = Program()
        for func in func_list:
            root.children.append(func)

        return root


    def function(self):
        '''function : type_spec variable LPAREN formal_param_list RPAREN block'''
        program_type = self.type_spec()
        program_name = self.variable().value
        self.eat(TokenType.LPAREN)
        program_params = self.formal_param_list()
        self.eat(TokenType.RPAREN)
        program_block = self.block()
        program_node = Function(
            type = program_type,
            name = program_name,
            formal_params = program_params,
            block = program_block
        )
        return program_node

    
    def type_spec(self):
        '''type_spec : INT | VOID'''
        token = self.current_token
        if self.current_token.type == TokenType.INT:
            self.eat(TokenType.INT)
        else:
            self.eat(TokenType.VOID)
        type_node = Type(token)
        return type_node


    def formal_param_list(self):
        '''formal_param_list : formal_param | VOID | EMPTY'''
        if self.current_token.type == TokenType.INT:
            # func(int a, int b)
            param_list = self.formal_param()
        elif self.current_token.type == TokenType.VOID:
            # func(void)
            token = self.current_token
            type_node = self.type_spec()
            param_list = [Param(Var(token), type_node)]
        else:
            # func()
            param_list = [NoOp()]
        # param_nodes: [Param(var, type), Param(TokenType.VOID, TokenType.VOID)]
        return param_list
    

    def formal_param(self):
        '''formal_param : INT ID ( COMMA INT ID )*'''
        # for simplicity, we can omit compute type_node, which is INT
        # but for future type extension, we keep compute type_node each-time
        type_node = self.type_spec()
        # a list of params : formal_param
        param_list = [Param(Var(self.current_token), type_node)]
        self.eat(TokenType.ID)
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            type_node = self.type_spec()
            param_list.append(Param(Var(self.current_token), type_node))
            self.eat(TokenType.ID)
        
        return param_list
    

    def block(self):
        '''block : LBRACE declarations compound_statement RBRACE'''
        self.eat(TokenType.LBRACE)
        declarations = self.declarations()
        compound_statement = self.compound_statement()
        self.eat(TokenType.RBRACE)
        block_node = Block(
            declarations = declarations,
            compound_statement = compound_statement
        )
        return block_node


    def declarations(self):
        '''declarations : empty | ( variable_declaration SEMI )*'''
        declaration_list = []

        '''
        within this grammar-rule, we can only define something like,
        i.e. int a;
        instead of
        i.e. int a,b;
        '''

        # INT is the only available type in this interpreter
        while self.current_token.type == TokenType.INT:
            variable_declaration = self.variable_declaration()
            declaration_list.append(variable_declaration)
            self.eat(TokenType.SEMI)
        
        # if list is empty, append one NoOp node
        if not declaration_list:
            declaration_list.append(NoOp())

        root = Declaration()
        for declaration in declaration_list:
            root.children.append(declaration)
        
        return root


    def empty(self):
        return NoOp()


    def variable_declaration(self):
        '''variable_declaration : INT ID'''
        type_node = self.type_spec()
        var_node = Var(self.current_token)
        self.eat(TokenType.ID)
        vardecl_node = VarDecl(var_node, type_node)
        return vardecl_node


    def compound_statement(self):
        '''compound_statement : ( statement )+'''
        statement_list = []

        while self.current_token.type == TokenType.ID  \
            or self.current_token.type == TokenType.RETURN \
            or self.current_token.type == TokenType.IF \
            or self.current_token.type == TokenType.WHILE:
            # details for coresponding statement
            statement = self.statement()
            statement_list.append(statement)
        
        # if list is empty, append one NoOp node
        if not statement_list:
            statement_list.append(NoOp())

        root = Compound()
        for statement in statement_list:
            root.children.append(statement)
        
        return root


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
        assign_node = Assign(
            left = left,
            op = token,
            right = right
        )
        return assign_node
    

    def variable(self):
        '''variable: ID'''
        node = Var(self.current_token)
        self.eat(TokenType.ID)
        return node
    

    def return_statement(self):
        '''return_statement : RETURN ( expr )? SEMI'''
        token = self.current_token
        self.eat(TokenType.RETURN)
        if self.current_token.type != TokenType.SEMI:
            # return a;
            # return a+b/2-1;
            expr = self.expr()
        else:
            # return ;
            expr = NoOp()
        self.eat(TokenType.SEMI)
        
        return_node = Return(
            op = token,
            expr = expr
        )
        return return_node


    def while_statement(self):
        '''while_statement : WHILE LPAREN expr RPAREN block'''
        token = self.current_token
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        expr = self.expr()
        self.eat(TokenType.RPAREN)
        block = self.block()

        while_node = While(
            op = token,
            expr = expr,
            block = block
        )
        return while_node


    def if_statement(self):
        '''if_statement : IF LPAREN expr RPAREN block ( ELSE block )?'''
        token = self.current_token
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        expr = self.expr()
        self.eat(TokenType.RPAREN)
        if_block = self.block()

        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            else_block = self.block()
        else:
            else_block = NoOp()
        
        if_node = If(
            op = token,
            expr = expr,
            if_block = if_block,
            else_block = else_block
        )
        return if_node

    
    def expr(self):
        '''expr : relop_term ( relop relop_term )*'''
        node = self.relop_term()
        while self.current_token.type in (
            TokenType.LT, 
            TokenType.LTE, 
            TokenType.LG, 
            TokenType.LGE, 
            TokenType.EQUAL, 
            TokenType.NOT_EQUAL
        ):
            token = self.relop()
            node = BinOp(
                left = node,
                op = token,
                right = self.relop_term()
            )

        return node    


    def relop(self):
        '''relop : LT | LTE | LG | LGE | EQUAL | NOT_EQUAL'''
        token = self.current_token
        self.eat(self.current_token.type)
        return token


    def relop_term(self):
        '''relop_term : term ( (PLUS | MINUS) term )*'''
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)

            node = BinOp(
                left = node, 
                op = token, 
                right = self.term()
            )

        return node
    

    def term(self):
        '''term : factor ( (MUL | DIV) factor )*'''
        node = self.factor()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)

            node = BinOp(
                left = node, 
                op = token, 
                right = self.factor()
            )

        return node


    def factor(self):
        '''factor : INTEGER_CONST | LPAREN expr RPAREN | ID | proccall'''
        token = self.current_token
        if token.type == TokenType.INTEGER_CONST:
            self.eat(TokenType.INTEGER_CONST)
            return Num(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.ID and self.lexer.current_char == '(':
            node = self.proccall()
        elif token.type == TokenType.ID:
            node = self.variable()
        else:
            node = self.empty()
            self.error(
                error_code=ErrorCode.UNEXPECTED_TOKEN,
                token=self.current_token
            )
        return node
    
    def proccall(self):
        '''proccall : ID LPAREN ( expr ( COMMA expr )* )? RPAREN'''
        token = self.current_token
        proc_name = token.value

        self.eat(TokenType.ID)
        self.eat(TokenType.LPAREN)

        actual_params = []
        
        # func()
        # func(4)
        if self.current_token.type != TokenType.RPAREN:
            node = self.expr()
            actual_params.append(node)
        
        # func(a,b,4*5)
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            node = self.expr()
            actual_params.append(node)
        
        if not actual_params:
            actual_params.append(NoOp())
        
        self.eat(TokenType.RPAREN)

        node = ProcedureCall(
            name = proc_name,
            actual_params = actual_params,
            token = token
        )
        return node
        
    
    def parse(self):
        '''
        program                 : type_spec variable LPAREN formal_param_list RPAREN block

        type_spec               : INT | VOID

        formal_param_list       : formal_param | VOID | EMPTY

        formal_param            : INT ID ( COMMMA INT ID )*

        block                   : LBRACE declarations compound_statement RBRACE

        declarations            : empty | ( variable_declaration SEMI )*

        empty                   :

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

        factor                  : INTEGER_CONST | LPAREN expr RPAREN | ID | proccall

        proccall                : ID LPAREN ( expr ( COMMA expr )* )? RPAREN
        
        variable                : ID

        '''
        node = self.program()
        if self.current_token.type != TokenType.EOF:
            self.error(
                error_code = ErrorCode.UNEXPECTED_TOKEN,
                token = self.current_token
            )

        return node
    

    def parseProcCall(self):
        '''
        program                 : ( type_spec variable SEMI | type_spec variable LPAREN formal_param_list RPAREN block )+

        function                : type_spec variable LPAREN formal_param_list RPAREN block

        type_spec               : INT | VOID

        formal_param_list       : formal_param | VOID | EMPTY

        formal_param            : INT ID ( COMMMA INT ID )*

        block                   : LBRACE declarations compound_statement RBRACE

        declarations            : empty | ( variable_declaration SEMI )*

        empty                   :

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

        factor                  : INTEGER_CONST | LPAREN expr RPAREN | ID | proccall

        proccall                : ID LPAREN ( expr ( COMMA expr )* )? RPAREN

        variable                : ID

        '''
        node = self.program()

        if self.current_token.type != TokenType.EOF:
            self.error(
                error_code = ErrorCode.UNEXPECTED_TOKEN,
                token = self.current_token
            )

        return node


### AST Visitor
class NodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))
