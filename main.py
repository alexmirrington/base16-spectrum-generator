import sys
import numpy as np
import os.path
from PIL import Image
import yaml

def main(theme_file, out_file):
    theme = None

    try:
        with open(theme_file, 'r') as f:
            theme = yaml.safe_load(f)
    except OSError:
        print('Unable to open file at {0}'.format(theme_file))
    except yaml.scanner.ScannerError:
        print('Unable to parse file at {0}'.format(theme_file))

    colours = []

    for k, v in theme.items():
        if 'base' not in k:
            continue

        col = parse_hex(v)

        if col != None:
            colours.append(col)

    # TODO put these values in params
    width = 800
    height = 100
    pixels = generate_pixels(colours, width, height)

    Image.fromarray(pixels, mode='RGB').save(out_file)

def generate_pixels(colours: list, width: int, height: int):
    block_width = int(width/len(colours))
    block_remainder = width % len(colours)

    for i, c in enumerate(colours):
        colour = np.array(c, dtype=np.uint8)
        print(colour)
        if i == 0:
            pixels = np.tile(colour, (height, block_width + block_remainder, 1))
            continue
        block = np.tile(colour, (height, block_width, 1))
        pixels = np.concatenate((pixels, block), axis=1)

    return pixels

def parse_hex(value: str):
    try:
        val = int(value, base=16)
    except:
        return None
    r = (val & 0xFF0000) >> 16
    g = (val & 0x00FF00) >> 8
    b = (val & 0x0000FF) >> 0
    return (r, g, b)

def parse_args(args: list):
    if (len(args) != 3):
        print_help()
        return

    if not os.path.exists(args[1]):
        print('Invalid theme file. Please ensure the directory exists and it is a correctly formatted .yaml file.')
        return

    return {
        'theme_file': args[1],
        'out_file': args[2]
    }

def print_help():
    print('Usage: python main.py <theme_file> <output_file>')

if __name__ == "__main__":
    parsed_args = parse_args(sys.argv)
    if (parsed_args != None):
        main(parsed_args.get('theme_file'), parsed_args.get('out_file'))