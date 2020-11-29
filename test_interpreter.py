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
    
    def test_lexererr(self):
        from Lexer import TokenType
        testcase = [
            (
                '''
                void main(void)
                {
                    %
                }
                ''',
                [
                    "\'%\' is not a valid TokenType",
                    'LexerError: Lexer error on \'%\' line: 4 column: 21'
                ]
            )
        ]
        for text, err in testcase:
            lexer = self.buildLexer(text)
            token = lexer.get_next_token()
            while token.type != TokenType.EOF and token.type != None:
                token = lexer.get_next_token()
        
            for Err, assertErr in zip(lexer.getErrList(), err):
                self.assertEqual(Err.__str__(), assertErr)
    
    def test_getalltokens(self):
        from Lexer import Token, TokenType
        text, assertTokenList = (
            '''
            void main(void)
            {
                %
            }
            ''',
            [
                Token(TokenType.ID, 'main', lineno=2,column=18),
                Token(TokenType.LPAREN, '(', lineno=2,column=22),
                Token(TokenType.VOID, 'VOID', lineno=2,column=23),
                Token(TokenType.RPAREN, ')', lineno=2,column=27),
                Token(TokenType.LBRACE, '{', lineno=3,column=13),
                Token(None, None, lineno=None,column=None)
            ]
        )
        lexer = self.buildLexer(text)
        RetValue, token_list = lexer.get_all_tokens()
        self.assertFalse(RetValue)
        for token, assertToken in zip(token_list, assertTokenList):
            self.assertEqual(token.type, assertToken.type)

    def disabled_test_notation_removal(self):
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
                ["ParserError: Unexpected token -> Token(TokenType.INT, 'INT', position=5:18)"]
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
                ["ParserError: Unexpected token -> Token(None, None, position=4:21)"]
            )
        ]

        for text, err in testcase:
            interpreter = self.buildParser(text)
            interpreter.parseProcCall()
            for err, assertErr in zip(interpreter.getErrList(), err):
                self.assertEqual(err.__str__(), assertErr)


if __name__ == '__main__':
    unittest.main()