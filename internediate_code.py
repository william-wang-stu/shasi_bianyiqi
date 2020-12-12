from Parser import NodeVisitor

class ThreeAddressCode:
    def __init__(self, left=None, right=None, op=None, result=None):
        self.left = left
        self.right = right
        self.op = op
        self.result = result
    def __str__(self):
        if self.left is None:
            return f'({self.result:>5},  NoOp, {self.op:>5}, {self.right:>5})'
        return f'({self.result:>5}, {self.left:>5}, {self.op:>5}, {self.right:>5})'

class JumpBlockCode:
    def __init__(self, code):
        self.code = code
    def __str__(self):
        return f'{self.code}'

# todo: if, while, return, proccall

class IRGenerator(NodeVisitor):
    '''
    Intermediate Representation Generator
        input:  Abstract Syntax Tree
        output: 3-address code sequence
    '''
    def __init__(self, parser):
        super().__init__()
        self.parser = parser
        self.code = []
        self.retaddr = None
        self._tempcount = 0
        self._signcount = 0
    
    def newtemp(self, type):
        '''
        i.e. temporary variable: int_1, float_2
        temporary sign for jump code: nxt_3, jmp_4
        '''
        if type in ('int', 'float'):
            tempname = "%s_%d" % (type, self._tempcount)
            self._tempcount += 1
        elif type in ('nxt', 'jmp'):
            tempname = "%s_%d" % (type, self._signcount)
            self._signcount += 1
        return tempname

    def visit_Var(self, node):
        # i.e. a, b, c
        return node.value

    def visit_NoOp(self, node):
        pass

    def visit_Type(self, node):
        pass

    def visit_Param(self, node):
        self.visit(node.var)
        self.visit(node.type)

    def visit_BinOp(self, node):
        # temporarily put node.place in return value
        leftAddress = self.visit(node.left)
        rightAddress = self.visit(node.right)
        # create new temp, i.e. int_1, float_2
        # set int as default type
        resultAddress = self.newtemp('int')
        # gen
        binop_instr = ThreeAddressCode(
            left = leftAddress,
            right = rightAddress,
            op = node.op.value, # TokenType.PLUS.value = '+'
            result = resultAddress
        )
        self.code.append(binop_instr)
        # save node.place in return value
        return resultAddress

    def visit_Num(self, node):
        # i.e. 372, 519
        return node.value

    def visit_Program(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Function(self, node):
        self.visit(node.type)
        for param_node in node.formal_params:
            self.visit(param_node)
        self.visit(node.block)
    
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
        # temporarily put node.place in return value
        leftAddress = self.visit(node.left)
        rightAddress = self.visit(node.right)
        # gen
        binop_instr = ThreeAddressCode(
            right = rightAddress,
            op = node.token.value, # TokenType.PLUS.value = '+'
            result = leftAddress
        )
        self.code.append(binop_instr)

    def visit_Return(self, node):
        self.visit(node.expr)
        if self.retaddr is not None:
            callFuncRet = JumpBlockCode(code = f'goto {self.retaddr}')
            self.retaddr = None

    def visit_While(self, node):
        # gen new temp
        beginAddress = self.newtemp('jmp')
        nextAddress = self.newtemp('nxt')

        beginAddressSign = JumpBlockCode(code = f'{beginAddress}:')
        self.code.append(beginAddressSign)

        # E.place
        exprAddress = self.visit(node.expr)
        while_instr = JumpBlockCode(code = f'if {exprAddress} = 0 goto {nextAddress}')
        self.code.append(while_instr)
        self.visit(node.block)

        jumpBackBlock = JumpBlockCode(code = f'goto {beginAddress}')
        self.code.append(jumpBackBlock)
        nextAddressSign = JumpBlockCode(code = f'{nextAddress}:')
        self.code.append(nextAddressSign)


    def visit_If(self, node):
        # E.place
        exprAddress = self.visit(node.expr)
        # gen new temp
        trueAddress = self.newtemp('jmp')
        if type(node.else_block).__name__ != 'NoOp':
            falseAddress = self.newtemp('jmp')
        nextAddress = self.newtemp('nxt')
        # i.e. if expr = 1 goto trueAddress
        if_instr = JumpBlockCode(code = f'if {exprAddress} = 1 goto {trueAddress}')
        self.code.append(if_instr)
        # i.e. goto falseAddress
        if type(node.else_block).__name__ != 'NoOp':
            falseAddressSign = JumpBlockCode(code = f'goto {falseAddress}')
            self.code.append(falseAddressSign)
        
        '''
        ( if-block )
        trueAddressSign: { if-block }
        goto falseAddress
        '''
        trueAddressSign = JumpBlockCode(code = f'{trueAddress}:')
        self.code.append(trueAddressSign)
        self.visit(node.if_block)
        jumpAfterBlock = JumpBlockCode(code = f'goto {nextAddress}')
        self.code.append(jumpAfterBlock)

        # else-block
        if type(node.else_block).__name__ != 'NoOp':
            falseAddressSign = JumpBlockCode(code = f'{falseAddress}:')
            self.code.append(falseAddressSign)
            self.visit(node.else_block)
        
        # next Address Sign
        nextAddressSign = JumpBlockCode(code = f'{nextAddress}:')
        self.code.append(nextAddressSign)

    def visit_VarDecl(self, node):
        pass

    def visit_ProcedureCall(self, node):
        print(f'...encounter procedure call: {node.name} ...')
        proccallSign = JumpBlockCode(code = f'{node.name}:')
        self.code.append(proccallSign)
        for param_node in node.actual_params:
            self.visit(param_node)
        proccall = JumpBlockCode(code = f'call {node.name}')
        self.code.append(proccall)
        self.retaddr = node.name
        # factor : proccall (parser)
        # save node.place in return value
        return self.retaddr

    def genCodeSeq(self):
        astTree = self.parser.parseProcCall()
        self.visit(astTree)

