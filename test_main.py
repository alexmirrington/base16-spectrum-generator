import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from PIL import Image
import yaml

from main import main


class ThemeFormatsTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.palette = {"base{:02X}".format(i): "{:06x}".format(i * 0x010101)
                        for i in range(16)}

    def render(self, data, name):
        theme_file = self.root / (name + ".yaml")
        output_file = self.root / (name + ".png")
        theme_file.write_text(yaml.safe_dump(data, sort_keys=False))
        with contextlib.redirect_stdout(io.StringIO()):
            main(theme_file, output_file)
        return output_file

    def test_legacy_and_nested_palettes_render_the_same_spectrum(self):
        flat = {"scheme": "Fixture", "author": "Test", **self.palette}
        nested = {"name": "Fixture", "author": "Test", "palette": self.palette}
        with Image.open(self.render(flat, "legacy")) as legacy:
            with Image.open(self.render(nested, "nested")) as current:
                self.assertEqual(legacy.size, (800, 100))
                self.assertEqual(legacy.mode, "RGB")
                self.assertEqual(legacy.tobytes(), current.tobytes())
                for i in range(16):
                    self.assertEqual(legacy.getpixel((i * 50, 0)), (i, i, i))

    def test_explicit_palette_takes_precedence_over_flat_keys(self):
        data = {"base00": "ffffff", "palette": self.palette}
        with Image.open(self.render(data, "precedence")) as image:
            self.assertEqual(image.getpixel((0, 0)), (0, 0, 0))

    def test_malformed_or_empty_palettes_do_not_create_an_image(self):
        cases = [None, [], 123, "not a mapping", {}, {"palette": None},
                 {"palette": []}, {"palette": "not a mapping"},
                 {"palette": {}}, {"palette": {"base00": "not hex"}},
                 {"palette": {123: "ffffff"}}]
        cases.extend({"palette": {"base00": value}}
                     for value in [None, 123, True, [], {}])
        for i, data in enumerate(cases):
            with self.subTest(data=data):
                self.assertFalse(self.render(data, "invalid-{}".format(i)).exists())

    def test_malformed_yaml_does_not_create_an_image(self):
        theme_file = self.root / "broken.yaml"
        output_file = self.root / "broken.png"
        theme_file.write_text("palette: [\n")
        with contextlib.redirect_stdout(io.StringIO()):
            main(theme_file, output_file)
        self.assertFalse(output_file.exists())


if __name__ == "__main__":
    unittest.main()
