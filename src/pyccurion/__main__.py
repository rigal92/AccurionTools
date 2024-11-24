import sys
from pyccurion import readROIdat, accurionToWase, readImage

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser("")
    parser.add_argument("--wase", dest="towase", action="store_true", help="convert the file to be openable from wase")
    parser.add_argument("--image", dest="image", action="store_true", help="read image and convert to array")
    parser.add_argument('filename', nargs=1, help='name of the file')
    args = parser.parse_args()
    towase = args.towase
    image = args.image
    filename = args.filename[0]
    if not (towase or image):
        print("Missing flag")
    if towase:
        print("Splitting file" )
        accurionToWase(filename)
    if image:
        readImage(filename)
