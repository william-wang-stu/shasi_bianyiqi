from Parser import NodeVisitor

#cur line number
cur_line = 100 - 1 

#to record all functions declared in Program 
class function_tbl_entry:
    def __init__(self,name,func_type):
        self.name = name
        self.func_type = func_type
        self.return_num = 0

function_tbl = []


class ThreeAddressCode:
    def __init__(self, left=None, right=None, op=None, result=None):
        self.left = left
        self.right = right
        self.op = op
        self.result = result
    def __str__(self):
        global cur_line
        cur_line = cur_line + 1
        if self.left is None:
            return f'{cur_line} : ( {self.op:>5},  NoOp,  {self.right:>5}, {self.result:>5})'
        return f'{cur_line} : ( {self.op:>5}, {self.left:>5},  {self.right:>5},{self.result:>5})'

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
        #record the return value in the declr of functions
        self.cur_func = None

        self._tempcount = 0
        self._signcount = 0
        self._funccount = 0

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
        else:
            tempname = "%s_%s" % (type, "tmp")
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
        '''
        add function declarations
        FUNC (PARMAS) BLOCK
        '''
        # print(f'...encounter Function: {node.name} ...')
        # record the function and reset the num of temp reg for return value  
        self.cur_func = node.name
        
        # add a startAddr for func
        beginAddressSign = JumpBlockCode(code = f'{node.name}:')
        self.code.append(beginAddressSign)

        #need to check if error
        function_tbl.append(function_tbl_entry(node.name, node.type))

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
        return leftAddress

    def visit_Return(self, node):
        '''
        For return value in function delclarations
        save the return val in a temp reg named {self.function}
        '''
        # the final reg addr of expr
        resultAddr = self.visit(node.expr)

        if self.retaddr is not None:
            callFuncRet = ThreeAddressCode(
                                op = 'j',
                                left= '-',
                                right = '-',
                                result = self.retaddr
                            )#JumpBlockCode(code = f'goto {self.retaddr}')
            
            self.retaddr = None

        if resultAddr is not None:
            # temp reg for return value 
            resultAddress = self.newtemp(self.cur_func)
            # assign the return value from a shared reg(in the func declr) to real value in the Program 
            return_instr = ThreeAddressCode(
                right = resultAddr,
                op = '=',
                result = resultAddress
            )
            self.code.append(return_instr)
        
         
    def visit_While(self, node):
        # gen new temp
        beginAddress = self.newtemp('jmp')
        nextAddress = self.newtemp('nxt')

        # jmp_0: the beginning of condition
        beginAddressSign = JumpBlockCode(code = f'{beginAddress}:')
        self.code.append(beginAddressSign)

        # E.place - iteration for expr  
        exprAddress = self.visit(node.expr)

        while_instr = ThreeAddressCode(
                                op = 'jz',
                                left= exprAddress,
                                right = '-',
                                result = nextAddress
                            ) # JumpBlockCode(code = f'if {exprAddress} = 0 goto {nextAddress}')
                    
                        
        self.code.append(while_instr)

        # iteration for block 
        self.visit(node.block)

        jumpBackBlock = ThreeAddressCode(
                                op = 'j',
                                left= '-',
                                right = '-',
                                result = beginAddress
                            )#JumpBlockCode(code = f'goto {beginAddress}')
        
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
        
        if_instr = ThreeAddressCode(
                                op = 'jnz',
                                left= exprAddress,
                                right = '-',
                                result = trueAddress
                            ) 
        # JumpBlockCode(code = f'if {exprAddress} = 1 goto {trueAddress}')
        self.code.append(if_instr)
        # i.e. goto falseAddress
        if type(node.else_block).__name__ != 'NoOp':
            #falseAddressSign = JumpBlockCode(code = f'goto {falseAddress}')

            else_instr = ThreeAddressCode(
                                op = 'j',
                                left= '-',
                                right = '-',
                                result = falseAddress
                            )

            self.code.append(else_instr)
        
        '''
        ( if-block )
        trueAddressSign: { if-block }
        goto falseAddress
        '''
        trueAddressSign = JumpBlockCode(code = f'{trueAddress}:')
        self.code.append(trueAddressSign)
        self.visit(node.if_block)
        jumpAfterBlock = ThreeAddressCode(
                                op = 'j',
                                left= '-',
                                right = '-',
                                result = nextAddress
                            )#JumpBlockCode(code = f'goto {nextAddress}')

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
        '''
        
        '''
        #print(f'...encounter procedure call: {node.name} ...')
        global function_tbl

        #add parms before the call
        # i.e.
        # Param a
        # Param b
        # Param c
        # call demo
        for param_node in node.actual_params:
            node_value = self.visit(param_node)
            self.code.append(f'Param {node_value}')
        
        # call the func
        proccall = JumpBlockCode(code = f'call {node.name}')
        self.code.append(proccall)
        
        # get a temp reg for the procedureCall
        temp_name = node.name+"_tmp"

        # check if the function has a return value 
        for entry in function_tbl: # we assume that there is no overload for function! 
            if entry.name == node.name:
                if entry.func_type != 'VOID':
                    # temp reg for return value 
                    temp_reg = "%s_%d" % (temp_name, entry.return_num)
                    entry.return_num += 1
                    # assign the value from a shared reg(in the func declr) to real value in the Program 
                    # i.e. (     =,  NoOp,  demo_tmp, demo_tmp_0)
                    return_instr = ThreeAddressCode(
                        right = temp_name,
                        op = '=',
                        result = temp_reg
                    )
                    
                    self.code.append(return_instr)

                    self.retaddr = temp_reg
                break
        # factor : proccall (parser)
        # save node.place in return value
        return self.retaddr

    def genCodeSeq(self):
        astTree = self.parser.parseProcCall()
        self.visit(astTree)

