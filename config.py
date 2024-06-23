import sys
from os import path

project_root = path.abspath(path.dirname(__file__))
sys.path.append(path.join(project_root, 'classes'))
sys.path.append(path.join(project_root, 'mylibs'))

if __name__ == "__main__":
    print(sys.path)