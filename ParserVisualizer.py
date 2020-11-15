import textwrap

from Parser import NodeVisitor

class ASTVisualizer(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.ncount = 1
        self.dot_header = [textwrap.dedent("""\
        digraph astgraph {
          node [shape=circle, fontsize=12, fontname="Courier", height=.1];
          ranksep=.3;
          edge [arrowsize=.5]

        """)]
        self.dot_body = []
        self.dot_footer = ['}']
    
    def visit_Var(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_NoOp(self, node):
        s = '  node{} [label="NoOp"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_Type(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.token.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_Param(self, node):
        s = '  node{} [label="Param"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.var)
        s = '  node{} -> node{}\n'.format(node._num, node.var._num)
        self.dot_body.append(s)

        self.visit(node.type)
        s = '  node{} -> node{}\n'.format(node._num, node.type._num)
        self.dot_body.append(s)

    def visit_BinOp(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.left)
        self.visit(node.right)

        for child_node in (node.left, node.right):
            s = '  node{} -> node{}\n'.format(node._num, child_node._num)
            self.dot_body.append(s)

    def visit_Num(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.token.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_Program(self, node):
        s = '  node{} [label="Program:{}"]\n'.format(self.ncount, node.name)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.type)
        s = '  node{} -> node{}\n'.format(node._num, node.type._num)
        self.dot_body.append(s)

        for param_node in node.formal_params:
            self.visit(param_node)
            s = '  node{} -> node{}\n'.format(node._num, param_node._num)
            self.dot_body.append(s)

        self.visit(node.block)
        s = '  node{} -> node{}\n'.format(node._num, node.block._num)
        self.dot_body.append(s)
    
    def visit_Block(self, node):
        s = '  node{} [label="Block"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.declarations)
        s = '  node{} -> node{}\n'.format(
            node._num,
            node.declarations._num
        )
        self.dot_body.append(s)

        self.visit(node.compound_statement)
        s = '  node{} -> node{}\n'.format(
            node._num,
            node.compound_statement._num
        )
        self.dot_body.append(s)

    def visit_Declaration(self, node):
        s = '  node{} [label="Declr"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for child in node.children:
            self.visit(child)
            s = '  node{} -> node{}\n'.format(node._num, child._num)
            self.dot_body.append(s)

    def visit_Compound(self, node):
        s = '  node{} [label="Compound"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for child in node.children:
            self.visit(child)
            s = '  node{} -> node{}\n'.format(node._num, child._num)
            self.dot_body.append(s)

    def visit_Assign(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.left)
        self.visit(node.right)

        for child_node in (node.left, node.right):
            s = '  node{} -> node{}\n'.format(node._num, child_node._num)
            self.dot_body.append(s)

    def visit_Return(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.expr)
        s = '  node{} -> node{}\n'.format(node._num, node.expr._num)
        self.dot_body.append(s)

    def visit_While(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.expr)
        s = '  node{} -> node{}\n'.format(node._num, node.expr._num)
        self.dot_body.append(s)

        self.visit(node.block)
        s = '  node{} -> node{}\n'.format(node._num, node.block._num)
        self.dot_body.append(s)

    def visit_If(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.expr)
        s = '  node{} -> node{}\n'.format(node._num, node.expr._num)
        self.dot_body.append(s)

        self.visit(node.if_block)
        s = '  node{} -> node{}\n'.format(node._num, node.if_block._num)
        self.dot_body.append(s)

        self.visit(node.else_block)
        s = '  node{} -> node{}\n'.format(node._num, node.else_block._num)
        self.dot_body.append(s)

    def visit_VarDecl(self, node):
        s = '  node{} [label="VarDecl"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.var)
        s = '  node{} -> node{}\n'.format(node._num, node.var._num)
        self.dot_body.append(s)

        self.visit(node.type)
        s = '  node{} -> node{}\n'.format(node._num, node.type._num)
        self.dot_body.append(s)

    def visit_ProcedureCall(self, node):
        s = '  node{} [label="ProcCall:{}"]\n'.format(
            self.ncount,
            node.name
        )
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for param_node in node.actual_params:
            self.visit(param_node)
            s = '  node{} -> node{}\n'.format(node._num, param_node._num)
            self.dot_body.append(s)

    def gendot(self):
        '''
        parser = Parser(lexer)
        viz = ASTVisualizer(parser)
        content = viz.gendot()
        print(content)
        '''
        tree = self.parser.parse()
        self.visit(tree)
        return ''.join(self.dot_header + self.dot_body + self.dot_footer)
