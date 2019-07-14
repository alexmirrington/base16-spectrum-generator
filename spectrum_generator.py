import sys
import os.path
import png
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
        if (len(colours) == 16):
            break
        col = parse_hex(v)
        # Hacky but will work fine for now. Not gonna make it more complicated than it needs to be
        if col != None:
            colours.append(col)

    # TODO put these values in params
    width = 800
    height = 100
    pixels = generate_pixels(colours, width, height)
    png.from_array(pixels, mode='RGB').save(out_file)

def generate_pixels(colours, width, height):
    pixels = [[colours[int(len(colours) * x / width)] for x in range(width)] for y in range(height)]
    return pixels

def parse_hex(value):
    try:
        val = int(value, base=16)
    except:
        return None
    r = (val & 0xFF0000) >> 16
    g = (val & 0x00FF00) >> 8
    b = (val & 0x0000FF) >> 0
    return (r, g, b)

def parse_args(args):
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
    print('Usage: spectrum_generator <theme_file> <output_file>')

if __name__ == "__main__":
    parsed_args = parse_args(sys.argv)
    if (parsed_args != None):
        main(parsed_args.get('theme_file'), parsed_args.get('out_file'))