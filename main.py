from Lexer import TokenType, Lexer
from notation_removal import notation_removal
from Parser import test

example_text_list = [
    # '24abc',
    # '24abc\n123',
    # '(abc){123}',
    # 'if123',
    # 'if=123',
    '''
    int main(){
        i<=j
        >= ==
        !=
        <>
    }
    ''',
    '''
    //  1435395742
    /*
    ifhe
    */
    1233
    '''
]

'''
int  program(int a,int b,int c)
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
	while(i<100)
	{
		i=j*2;
	}
	return i;
}
'''


if __name__ == '__main__':
    test()
    '''
    for example_text in example_text_list:
        print(f"Lexer for {example_text}:")
        example_text = notation_removal(example_text)
        lexer = Lexer(example_text)
        while True:
            token = lexer.get_next_token()
            if token.type == TokenType.EOF:
                break
            print(token)
    '''

    '''
    while True:
        try:
            text = input('Lexer> ')
        except EOFError:
            break
        if not text:
            continue

        lexer = Lexer(text)
        while True:
            token = lexer.get_next_token()
            if token.type == TokenType.EOF:
                break
            print(token)
    '''
    