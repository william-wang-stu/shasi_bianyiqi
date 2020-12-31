from Lexer import TokenType, Lexer
from notation_removal import notation_removal
from Parser import Parser
from IntermediateCodeGenerator import IRGenerator
from SemanticAnalyzer import SemanticAnalyzer
from RunTimeAnalyzer import RuntimeAnalyzer

from ParserVisualizer import ASTVisualizer
if __name__ == '__main__':
	text = '''
		int a;
		int b;
		int program(int a,int b,int c)
		{
			int i;
			int j;
			i=0;
			j=1;
			return 10;
		}
		int demo(int a)
		{
			a=a+2;
			return a;
		}
		void main(void)
		{
			int a;
			int b;
			a=3;
			b=4;
			c=2;
			a=program(a,b,demo(c));
	'''
	lexer = Lexer(text)
	# parser = Parser(lexer)
	flag, token_list = lexer.get_all_tokens()
	for token in token_list:
		print(token)
	
	# viz = ASTVisualizer(parser)
	# content = viz.gendot()
	# print(content)
	
	# irg = IRGenerator(parser)
	# irg.genCodeSeq()
	# for instr in irg.code:
	# 	print(instr)

	'''
	tree = parser.parseProcCall()
	sm = SemanticAnalyzer()
	sm.visit(tree)
	for err in sm.getErrList():
		print(err)
	
	# tree = parser.parseProcCall()
	rt = RuntimeAnalyzer()
	rt.visit(tree)
	'''
