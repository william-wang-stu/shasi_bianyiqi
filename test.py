from Lexer import TokenType, Lexer
from notation_removal import notation_removal
from Parser import Parser
from internediate_code import IRGenerator

if __name__ == '__main__':
    text = '''
int a;
int b;
int program(int a,int b,int c)
{
	int i;
	int j;
	i=0; 	
	if(a>(b+c))
	{
		j=a+(b*c+1);
	}
	else
	{
		j=a;
	}
	while(i<=100)
	{
		i=j*2;
	}
	return i;
}

int demo(int a)
{
	a=a+2;
	return a*2;
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
    return ;
}
    '''
    '''
int program(int a,int b,int c)
{
	int i;
	int j;
	i=0; 	
	if(a>(b+c))
	{
		j=a+(b*c+1);
	}
	else
	{
		j=a;
	}
	while(i<=100)
	{
		i=j*2;
	}
	return i;
}
    '''
    lexer = Lexer(text)
    parser = Parser(lexer)
    irg = IRGenerator(parser)
    irg.genCodeSeq()

    for instr in irg.code:
        print(instr)
