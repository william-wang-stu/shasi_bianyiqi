from enum import Enum
from Lexer import TokenType
from Parser import NodeVisitor

MAIN_FUNC_NAME = 'main'
_LOG = False

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
        if _LOG:
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
        self.log(f'ENTER PROGRAM - global scope')
        ar = ActivationRecord(
            name = 'global',
            type = ActivationRecordType.PROGRAM,
            stacklvl = 0
        )
        self.call_stack.push(ar)
        self.log(str(self.call_stack))

        # visit subtree
        for child in node.children:
            self.visit(child)
        self.log(f'ENTER PROGRAM - global scope')
        self.log(str(self.call_stack))

        # reset stack
        self.call_stack.pop()

    def visit_Function(self, node):
        proc_name = node.name

        # return if it is only function decl
        if proc_name != MAIN_FUNC_NAME:
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
        return self.visit(node.compound_statement)

    def visit_Declaration(self, node):
        pass

    def visit_Compound(self, node):
        RetValue = None
        for child in node.children:
            RetValue = self.visit(child)
        return RetValue

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
        var_name = node.var.value
        ar = self.call_stack.peek()
        ar[var_name] = None

    def visit_ProcedureCall(self, node):
        proc_symbol = node.proc_symbol

        ar = ActivationRecord(
            name = node.name,
            type = ActivationRecordType.FUNCTION,
            stacklvl = proc_symbol.scope_level + 1
        )

        # first visit params
        formal_params = proc_symbol.formal_params
        actual_params = node.actual_params
        for formal_param, actual_param in zip(formal_params, actual_params):
            ar[formal_param.name] = self.visit(actual_param)
        
        # then push ar into stack frame
        self.call_stack.push(ar)
        self.log(f'ENTER: PROCEDURE {node.name}')
        self.log(str(self.call_stack))
        
        # calculate return value
        RetValue = self.visit(proc_symbol.block_ast)
        
        # finally pop from stack frame
        self.log(f'LEAVE: PROCEDURE {node.name}')
        self.log(str(self.call_stack))
        self.call_stack.pop()

        return RetValue

