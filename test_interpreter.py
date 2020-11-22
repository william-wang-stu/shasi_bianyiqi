import unittest

class ParserTestCase(unittest.TestCase):
    def buildParser(self, text):
        from Lexer import Lexer
        from Parser import Parser
        lexer = Lexer(text)
        parser = Parser(lexer)
        return parser
    
    def test_assignment(self):
        testcase = [
            (
                '''
void main(void)
{
	int a
	int b;
	int c;
	a = 3;
	b=4;
	c=2;
	a=program(a,b,demo(c));
	return ;
}
                ''',
                "ParserError: Unexpected token -> Token(TokenType.INT, 'INT', position=5:2)"
            ),
            (
                '''
void main(void)
{
    %
	int a;
	int b;
	int c;
	a = 3;
	b=4;
	c=2;
	a=program(a,b,demo(c));
	return ;
}
                ''',
                "LexerError: Lexer error on '%' line: 4 column: 5"
            )
        ]

        for text, error in testcase:
            interpreter = self.buildParser(text)
            with self.assertRaises(Exception) as context:
                interpreter.parseProcCall()
            # print(context.exception)
            self.assertTrue(error in str(context.exception))


if __name__ == '__main__':
    unittest.main()