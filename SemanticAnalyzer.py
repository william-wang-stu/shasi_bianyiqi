from enum import Enum
from Lexer import TokenType
from Parser import NodeVisitor
from Error_Detection import ErrorCode, SemanticError


class Symbol:
    def __init__(self, name, type = None):
        self.name = name
        self.type = type
        self.scope_level = 0


class VarSymbol(Symbol):
    def __init__(self, name, type):
        super().__init__(name, type)

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

    __repr__ = __str__


class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{class_name}(name='{name}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
        )


class ProcedureSymbol(Symbol):
    def __init__(self, node, formal_params = None):
        super().__init__(node.name)
        # add return value type for func i.e. INT demo
        self.type = node.type
        # a list of VarSymbol objects
        self.formal_params = [] if formal_params is None else formal_params
        # a reference to procedure's body (AST sub-tree)
        self.block_ast = None

    def __str__(self):
        return '<{class_name}(name={name}, parameters={params})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            params=self.formal_params,
        )

    __repr__ = __str__


class ScopedSymbolTable:
    def __init__(self, scope_name, scope_level, enclosing_scope = None):
        self._symbols = {}
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def _init_builtins(self):
        print("===== _init_builtins start =====")
        self.insert(BuiltinTypeSymbol('INT'))
        self.insert(BuiltinTypeSymbol('VOID'))
        print("===== _init_builtins finish =====")

    def __str__(self):
        prompt = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', prompt, '=' * len(prompt)]
        for header_name, header_value in (
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope', self.enclosing_scope.scope_name if self.enclosing_scope else None)
        ):
            lines.append(f'{header_name:<15}: {header_value}')
        prompt2 = 'Scope (Scoped symbol table) contents'
        lines.extend([prompt2, '-' * len(prompt2)])
        lines.extend(
            f'{key:>7}: {value}'
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s

    __repr__ = __str__

    def log(self, msg):
        if __debug__:
            print(msg)

    def insert(self, symbol):
        self.log(f'Insert: {symbol.name}') # {symbol.type}
        symbol.scope_level = self.scope_level
        self._symbols[symbol.name] = symbol

    def lookup(self, name, current_scope_only = False):
        # 'symbol' is either an instance of the Symbol class or None
        symbol = self._symbols.get(name)

        if symbol is not None:
            self.log(f'Lookup: {name}. (Scope name: {self.scope_name})')
            return symbol

        if current_scope_only:
            return None

        # recursively go up the chain and lookup the name
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)

        # self.log(f'Undefined variable : {name}.')


class SemanticAnalyzer(NodeVisitor):
    def __init__(self):
        self.current_scope = None

    def log(self, msg):
        if __debug__:
            print(msg)

    def error(self, error_code, token):
        raise SemanticError(
            error_code=error_code,
            token=token,
            message=f'{error_code.value} -> {token}',
        )

    def visit_Var(self, node):
        # self.log('enter visit_var')
        var_name = node.value
        # print("visit_Var", var_name)
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            self.error(error_code = ErrorCode.ID_NOT_FOUND, token = node.token)
        node.type = var_symbol.type
        # self.log('leave visit_var')

    def visit_NoOp(self, node):
        pass

    def visit_Type(self, node):
        pass

    def visit_Param(self, node):
        self.visit(node.var)
        self.visit(node.type)

    def visit_BinOp(self, node):
        # we have to judge whether node.left and node.right is of same type
        self.log('enter visit_binop')
        self.visit(node.left)
        self.visit(node.right)

        # here we dont need to perform type-check
        # bcz we have already done it in self.visit(node.*)
        if node.left.type != node.right.type:
            self.error(
                error_code=ErrorCode.TYPE_UNMATCHED,
                token=node.token,
            )
        node.type = node.left.type
        self.log('leave visit_binop')

    def visit_Num(self, node):
        # token: <type: TokenType.INTEGER_CONST, value: ~>
        # self.log('enter visit_num')
        if node.token.type == TokenType.INTEGER_CONST:
            node.type = 'INT'
        elif node.token.type == TokenType.REAL_CONST:
            node.type = 'FLOAT'
        else:
            node.type = None
        # self.log('leave visit_num')
    
    def visit_Program(self, node):
        # we assume the outest space is 'global' scope
        self.log('ENTER scope: global')
        global_scope = ScopedSymbolTable(
            scope_name = 'global',
            scope_level = 1,
            enclosing_scope = self.current_scope,  # None
        )
        global_scope._init_builtins()
        self.current_scope = global_scope

        # visit subtree
        for child in node.children:
            self.visit(child)

        # After we visit everything
        self.log(global_scope)
        self.log('LEAVE scope: global')

        # reset self.current_scope
        self.current_scope = self.current_scope.enclosing_scope

    def visit_Function(self, node):
        proc_name = node.name
        self.log(f'ENTER scope: {proc_name}')

        # add to the symbol table (current_scope->_symbols[symbol.name] = symbol
        proc_symbol = ProcedureSymbol(
            node = node,
        )
        self.current_scope.insert(proc_symbol)
        
        # enter a local scope
        procedure_scope = ScopedSymbolTable(
            scope_name = proc_name,
            scope_level = self.current_scope.scope_level + 1,
            # AKA last scope
            enclosing_scope = self.current_scope
        )
        self.current_scope = procedure_scope

        # Insert parameters into the procedure scope
        for param_node in node.formal_params:
            # we don't need to lookup var in the func declaration
            # self.current_scope.lookup(param_node.type.value)
            param_type = param_node.type.value
            if param_type != 'VOID':
                param_name = param_node.var.value
                var_symbol = VarSymbol(param_name, param_type)
                proc_symbol.formal_params.append(var_symbol)
                # also remind to insert param_varsymbol into current_scope (the local one)
                self.current_scope.insert(var_symbol)
        
        # visit block
        self.visit(node.block)

        # After we visit everything
        self.log(procedure_scope)
        self.log(f'LEAVE scope: {proc_name}')

        # reset self.current_scope
        self.current_scope = self.current_scope.enclosing_scope

        # accessed by the interpreter when executing procedure call
        proc_symbol.block_ast = node.block

    def visit_Block(self, node):
        self.visit(node.declarations)
        self.visit(node.compound_statement)

    def visit_Declaration(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        # we have to judge whether node.left and node.right is of same type
        self.log('enter visit_assign')
        self.visit(node.left)
        self.visit(node.right)

        # perform type-check, else raise error
        if node.left.type != node.right.type:
            self.error(
                error_code=ErrorCode.TYPE_UNMATCHED,
                token=node.token,
            )
        self.log('leave visit_assign')

    def visit_Return(self, node):
        self.visit(node.expr)

    def visit_While(self, node):
        self.visit(node.expr)
        self.visit(node.block)

    def visit_If(self, node):
        self.visit(node.expr)
        self.visit(node.if_block)
        if type(node.else_block).__name__ != 'NoOp':
            self.visit(node.else_block)

    def visit_VarDecl(self, node):
        # Create the symbol and insert it into the symbol table.
        self.log('enter visit_vardecl')
        type_name = node.type.value
        var_name = node.var.value
        var_symbol = VarSymbol(var_name, type_name)

        # Raise Error if the table already has a symbol with the same name
        if self.current_scope.lookup(var_name, current_scope_only = True):
            self.error(
                error_code=ErrorCode.DUPLICATE_ID,
                token=node.var_node.token,
            )

        # Else Insert it into the symbol table
        self.current_scope.insert(var_symbol)
        self.log('leave visit_vardecl')

    def visit_ProcedureCall(self, node):
        '''
        handle 3 possible errors:
        1. The num of formal-param and actual-param is different
        2. The num is correct, But param (if it is Var Object) is not declared
        3. The num is correct, But its type (Var or Num Object) is unmatched with Actual Params
        '''
        self.log(f'enter visit_proccall {node.name}')
        proc_symbol = self.current_scope.lookup(node.name)
        node.type = proc_symbol.type.value

        # address 1st error
        # use len() to detect length of list object
        if len(proc_symbol.formal_params) != len(node.actual_params):
            self.error(
                error_code=ErrorCode.PARAM_NUM_NOT_CONSISTENT,
                token=node.token
            )

        # address 2nd and 3rd error
        for idx, param_node in enumerate(node.actual_params):
            self.visit(param_node)
            # if actual params is of Var Object, we need to perform type-check and scope-lookup;
            # elif actual params is of Num Object, we only need to perform type-check
            # Here, we have already perform scope-lookup in self.visit(*)
            # So what we only need to do is type-check

            if param_node.type != proc_symbol.formal_params[idx].type:
                self.error(
                    error_code=ErrorCode.PROCALL_TYPE_UNMATCHED,
                    token=param_node.token,
                )
        
        # accessed by the interpreter when executing procedure call
        node.proc_symbol = proc_symbol
        self.log(f'leave visit_proccall {node.name}')


class ActivationRecordType(Enum):
    PROGRAM = 'PROGRAM'
    FUNCTION = 'FUNCTION'


class FuncStack:
    def __init__(self):
        self._records = []
    def push(self, ar):
        self._records.append(ar)
    def pop(self):
        return self._records.pop()
    def peek(self):
        return self._records[-1]
    def __str__(self):
        s = '\n'.join(repr(ar) for ar in reversed(self._records))
        s = f'CALL STACK\n{s}\n\n'
        return s
    def __repr__(self):
        return self.__str__()


class ActivationRecord:
    def __init__(self, name, type, stacklvl):
        self.name = name
        self.type = type
        self.stacklvl = stacklvl
        self.members = {}
    def __setitem__(self, key, value):
        self.members[key] = value
    def __getitem__(self, key):
        return self.members[key]
    def get(self, key):
        return self.members.get(key)
    def __str__(self):
        lines = [f'{self.stacklvl}: {self.type.value} {self.name}']
        for name, val in self.members.items():
            lines.append(f'   {name:<20}: {val}')
        s = '\n'.join(lines)
        return s
    def __repr__(self):
        return self.__str__()




class RuntimeAnalyzer(NodeVisitor):
    def __init__(self):
        self.call_stack = FuncStack()

    def log(self, msg):
        if __debug__:
            print(msg)

    def visit_Var(self, node):
        var_name = node.value
        ar = self.call_stack.peek()
        var_value = ar.get(var_name)
        return var_value

    def visit_NoOp(self, node):
        pass

    def visit_Type(self, node):
        pass

    def visit_Param(self, node):
        self.visit(node.var)
        self.visit(node.type)

    def visit_BinOp(self, node):
        if node.op.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == TokenType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == TokenType.DIV:
            return self.visit(node.left) / self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def visit_Program(self, node):
        # visit subtree
        for child in node.children:
            self.visit(child)

    def visit_Function(self, node):
        proc_name = node.name

        if proc_name != 'main':
            return

        self.log(f'ENTER FUNCTION: {proc_name}')
        # ActivationRecord Stack
        ar = ActivationRecord(
            name = proc_name,
            type = ActivationRecordType.FUNCTION,
            # we dont allow function be defined within another function
            stacklvl = 1
        )
        self.call_stack.push(ar)
        self.log(str(self.call_stack))

        # visit block
        self.visit(node.block)

        # After we visit everything
        self.log(f'LEAVE FUNCTION: {proc_name}')
        self.log(str(self.call_stack))

        # reset stack
        self.call_stack.pop()

    def visit_Block(self, node):
        self.visit(node.declarations)
        self.visit(node.compound_statement)

    def visit_Declaration(self, node):
        pass

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        var_name = node.left.value
        var_value = self.visit(node.right)

        # record the value in the function stack
        ar = self.call_stack.peek()
        ar[var_name] = var_value

    def visit_Return(self, node):
        return self.visit(node.expr)

    def visit_While(self, node):
        self.visit(node.expr)
        self.visit(node.block)

    def visit_If(self, node):
        self.visit(node.expr)
        self.visit(node.if_block)
        if type(node.else_block).__name__ != 'NoOp':
            self.visit(node.else_block)

    def visit_VarDecl(self, node):
        pass

    def visit_ProcedureCall(self, node):
        proc_symbol = node.proc_symbol

        ar = ActivationRecord(
            name = node.name,
            type = ActivationRecordType.FUNCTION,
            stacklvl = proc_symbol.scope_level + 1
        )

        formal_params = proc_symbol.formal_params
        actual_params = node.actual_params
        for formal_param, actual_param in zip(formal_params, actual_params):
            ar[formal_param.name] = self.visit(actual_param)

        self.call_stack.push(ar)
        self.log(f'ENTER: PROCEDURE {node.name}')
        self.log(str(self.call_stack))

        # evaluate procedure body
        ret = self.visit(proc_symbol.block_ast)
        print(ret)

        self.log(f'LEAVE: PROCEDURE {node.name}')
        self.log(str(self.call_stack))

        self.call_stack.pop()

