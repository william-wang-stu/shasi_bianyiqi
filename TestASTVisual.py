import argparse
import os

from Lexer import TokenType, Lexer
from notation_removal import notation_removal
from Parser import Parser
from ParserVisualizer import ASTVisualizer

# cmd: python TestASTVisual.py testfile.txt > ast.dot && dot -Tpng -o ast.png ast.dot

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Generate an AST DOT file.'
    )
    argparser.add_argument(
        'fname',
        help='Pascal source file'
    )
    args = argparser.parse_args()
    fname = args.fname
    text = open(fname, 'r').read()
    
    lexer = Lexer(text)
    parser = Parser(lexer)
    viz = ASTVisualizer(parser)
    content = viz.gendot()
    print(content)
