import io, json, os, tempfile, unittest
from contextlib import redirect_stdout
from todofind.cli import main, scan


class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        r = self.d.name
        os.makedirs(os.path.join(r, ".git"))
        os.makedirs(os.path.join(r, "node_modules"))
        w = lambda p, c, m="w": open(os.path.join(r, p), m).write(c)
        w("a.py", "x=1\n# TODO: fix this\n# FIXME broken\n")
        w("b.js", "// HACK: ugly\nvar s = 'no tag';\n")
        w(".git/c", "# TODO hidden\n")
        w("node_modules/d.js", "// TODO hidden\n")
        w("bin.dat", b"\0# TODO bin\n", "wb")

    def tearDown(self):
        self.d.cleanup()

    def run_cli(self, *args):
        b = io.StringIO()
        with redirect_stdout(b):
            code = main([self.d.name, *args])
        return code, b.getvalue()

    def test_scan_skips(self):
        self.assertEqual(len(scan(self.d.name)), 3)

    def test_output_format(self):
        _, out = self.run_cli("--tag", "todo")
        self.assertTrue(out.strip().endswith("a.py:2: TODO fix this"))
        self.assertEqual(len(out.strip().splitlines()), 1)

    def test_json(self):
        _, out = self.run_cli("--json")
        self.assertEqual({r["tag"] for r in json.loads(out)}, {"TODO", "FIXME", "HACK"})

    def test_fail(self):
        self.assertEqual(self.run_cli()[0], 0)
        self.assertEqual(self.run_cli("--fail")[0], 1)
        self.assertEqual(self.run_cli("--fail", "--tag", "XXX")[0], 0)


if __name__ == "__main__":
    unittest.main()
