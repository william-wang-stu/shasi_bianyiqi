from Lexer import TokenType, Lexer
from notation_removal import notation_removal
from Parser import Parser
from IntermediateCodeGenerator import IRGenerator
from SemanticAnalyzer import SemanticAnalyzer, RuntimeAnalyzer

from ParserVisualizer import ASTVisualizer
if __name__ == '__main__':
	text = '''
		int program(int a,int b,int c)
		{
			int i;
			int j;
			i=0;
			j=1;
		}
		int demo(int a)
		{
			a=a+2;
			return 2;
		}
		void main(void)
		{
			int a;
			int b;
			int c;
			a=3;
			b=4;
			c=2;
			a=program(a,b,demo(c));
		}
	'''
	lexer = Lexer(text)
	parser = Parser(lexer)
	
	# viz = ASTVisualizer(parser)
	# content = viz.gendot()
	# print(content)

	tree = parser.parseProcCall()
	sm = SemanticAnalyzer()
	sm.visit(tree)
	
	# rt = RuntimeAnalyzer()
	# rt.visit(tree)

	# sm = SemanticAnalyzer()
	# sm.visit(tree)

	'''
	irg = IRGenerator(parser)
	irg.genCodeSeq()
	for instr in irg.code:
		print(instr)
	'''

	# text = '''
	# 	int program(int a,int b,int c)
	# 	{
	# 		int i;
	# 		int j;
	# 		i=0;
	# 		j=1;
	# 	}
	# 	int demo(int a)
	# 	{
	# 		a=a+2;
	# 		return 2;
	# 	}
	# 	void main(void)
	# 	{
	# 		int a;
	# 		int b;
	# 		int c;
	# 		a=3;
	# 		b=4;
	# 		c=2;
	# 		a=program(a,b,demo(c));
	# 	}
	# '''