import unittest
import sys
import io

def stub_stdout(testcase_inst):
    stderr = sys.stderr
    stdout = sys.stdout

    def cleanup():
        sys.stderr = stderr
        sys.stdout = stdout
 
    testcase_inst.addCleanup(cleanup)
    sys.stderr = io.StringIO()
    sys.stdout = io.StringIO()

class LexerTestCase(unittest.TestCase):
    def buildLexer(self, text):
        from Lexer import Lexer
        from Parser import Parser
        lexer = Lexer(text)
        return lexer
    
    def test_notation_removal(self):
        testcase = [
            (
                '''
void main(void)
{
/*	int a
	int b;
	int c;
	a = 3;
	b=4;
	c=2;
	a=program(a,b,demo(c));
	return ;
}
                ''',
                "Error! illegal comment on row 4\n"
            ),
            (
                '''
void main(void)
{
/*	int a
	int b;*/
	int c;*/
	a = 3;
	b=4;
	c=2;
	a=program(a,b,demo(c));
	return ;
}
                ''',
                "Error! illegal comment on row 6\n"
            )
        ]
        
        from notation_removal import notation_removal
        for text, error in testcase:
            stub_stdout(self)
            text = notation_removal(text)
            self.assertEqual(str(sys.stdout.getvalue()), error)


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