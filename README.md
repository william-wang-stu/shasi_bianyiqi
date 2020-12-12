# shasi_bianyiqi

## Introduction
A simple C-like Interpreter

## Members
[张海](https://github.com/betray12138)  
[郑秋实](https://github.com/ZhengQiushi)  
[王泽鉴](https://github.com/william-wang-stu)

## Progress
11.04
- add notationn_removal function

11.05 
- add the detection for double char operation mark  by Truth
- Lexer Complete !

11.15
- Add `Parser.py`, `ParserTree.py`, `ParserVisualizer.py`
- Add `TestASTVisual.py`, `testfile.txt`, `ast.png`
- Parser Complete !

11.22
- Add LexerError and ParserError
- Add `test_interpreter.py` for unittest

12.12
- Add Semantic-Analyzer in `intermediate_code.py`: convert AST to three-address-code
- Add simple demo in `test.py` for Semantic-Analyzer

## Summary
11.15
- For starter, plz run `python main.py` or `python Interpreter.py testfile.txt False > ast.dot && dot -Tpng -o ast.png ast.dot`
- todos: 
   - Try more tests
   - Complement for class ParserError in `Error_Detection.py`
  
11.22
- Complete ParserError
- Add an arg `debug_mode` for interpreter to enable/disable traceback function in try-catch exception
- Add testfile `test_interpreter.py` for more interesting tests
- todos:
  - Add more tests
  - GUI

## References
Let’s Build A Simple Interpreter from Ruslan
https://ruslanspivak.com/lsbasi-part1/
