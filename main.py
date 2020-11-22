import os

# cmd: python Interpreter.py testfile.txt False > ast.dot && dot -Tpng -o ast.png ast.dot

if __name__ == '__main__':
    cmd = 'python Interpreter.py testfile.txt False > ast.dot && dot -Tpng -o ast.png ast.dot'
    os.system(cmd)
