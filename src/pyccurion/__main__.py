import sys
from pyccurion import readROIdat, accurionToWase

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser("")
    parser.add_argument("--wase", dest="towase", action="store_true", help="convert the file to be openable from wase")
    parser.add_argument('filename', nargs=1, help='name of the file')
    args = parser.parse_args()
    towase = args.towase
    filename = args.filename[0]
    if towase:
        accurionToWase(filename)