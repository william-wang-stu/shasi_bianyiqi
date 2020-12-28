from Lexer import TokenType 

class AST:
    pass


class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value
        # self.type would be updated in visit_var
        self.type = None


class NoOp(AST):
    pass


class Type(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Param(AST):
    '''
    parameter for functions
    '''
    def __init__(self, var, type):
        self.var = var
        self.type = type


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right
        # self.type should be updated in visit_binop
        self.type = None


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value
        # self.type should be updated in visit_num
        self.type = None


class Program(AST):
    def __init__(self):
        self.children = []


class Function(AST):
    def __init__(self, type, name, formal_params, block):
        '''
        parameter:
            type:           INT or VOID
            name:
            formal_params:  list of formal params
            block:
        '''
        self.type = type
        self.name = name
        self.formal_params = formal_params
        self.block = block


class Block(AST):
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement


class Declaration(AST):
    def __init__(self):
        self.children = []


class Compound(AST):
    def __init__(self):
        self.children = []


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Return(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class While(AST):
    def __init__(self, op, expr, block):
        self.token = self.op = op
        self.expr = expr
        self.block = block


class If(AST):
    def __init__(self, op, expr, if_block, else_block):
        self.token = self.op = op
        self.expr = expr
        self.if_block = if_block
        self.else_block = else_block


class VarDecl(AST):
    '''
    declare a var
    '''
    def __init__(self, var, type):
        self.var = var
        self.type = type


class ProcedureDecl(AST):
    def __init__(self, proc_name, formal_params, block_node):
        self.proc_name = proc_name
        self.formal_params = formal_params  # a list of Param nodes
        self.block_node = block_node


class ProcedureCall(AST):
    def __init__(self, name, actual_params, token):
        self.name = name
        # a list of Var object or Num object
        self.actual_params = actual_params
        self.token = token
        # a reference to procedure declaration symbol
        self.proc_symbol = None
        # to store what
        self.value = None
        self.type = None
