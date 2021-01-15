import sys

def load_file_from_cl():
    if len(sys.argv) < 2:
        return []
    path = sys.argv[1]
    lines = []
    with open(path) as f:
        data = f.read()
        lines= data.split('\n')
    return lines
