import argparse
import os
import sys

from Lexer import TokenType, Lexer
from notation_removal import notation_removal
from Parser import Parser
from ParserVisualizer import ASTVisualizer

# cmd: python Interpreter.py testfile.txt False > ast.dot && dot -Tpng -o ast.png ast.dot

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Generate an AST DOT file.'
    )
    argparser.add_argument(
        'fname',
        help='C-like source file'
    )
    argparser.add_argument(
        'debug_mode',
        help='Enable/Disable Traceback in Exception Error'
    )
    args = argparser.parse_args()
    fname = args.fname
    text = open(fname, 'r').read()

    if args.debug_mode == 'False':
        sys.tracebacklimit = 0
    
    lexer = Lexer(text)
    parser = Parser(lexer)
    viz = ASTVisualizer(parser)
    content = viz.gendot()
    print(content)

    for err in parser.getErrList():
        print(err.__str__())
