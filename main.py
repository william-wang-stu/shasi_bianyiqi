import os

# cmd: python TestASTVisual.py testfile.txt > ast.dot && dot -Tpng -o ast.png ast.dot

if __name__ == '__main__':
    cmd = 'python TestASTVisual.py testfile.txt > ast.dot && dot -Tpng -o ast.png ast.dot'
    os.system(cmd)
