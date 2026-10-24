import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

spec = importlib.util.spec_from_file_location("checker", Path(__file__).resolve().parents[1] / "scripts/check_docs.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class DocumentationChecks(unittest.TestCase):
    def test_mismatched_table_columns(self):
        _, _, errors = checker.render_document("| A | B |\n| --- | --- |\n| one | two | extra |\n")
        self.assertTrue(any("3 columns" in error for error in errors))

    def test_table_inline_code_and_escaped_pipes(self):
        _, _, errors = checker.render_document("| A | B |\n| --- | --- |\n| §a|b§ | one\\|two |\n".replace("§", chr(96)))
        self.assertEqual(errors, [])

    def test_code_examples_are_not_links_or_tables(self):
        fence = chr(96) * 3
        _, parsed, errors = checker.render_document(f"{fence}text\n[example](missing.md)\n| not a table\n{fence}\n")
        self.assertEqual(errors, [])
        self.assertEqual(parsed.links, [])

    def test_unclosed_code_fence(self):
        _, _, errors = checker.render_document(chr(96) * 3 + "bash\ngit status\n")
        self.assertIn("Unclosed Markdown code block", errors)

    def test_image_alt_text(self):
        _, _, errors = checker.render_document("![](photo.png)\n")
        self.assertIn("Image has no alternative text", errors)

    def test_nested_documents_and_anchor_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "README.md").write_text("[Guide](docs/guide.md#alias)\n", encoding="utf-8")
            (root / "docs/guide.md").write_text('<a name="alias"></a>\n\n# Topic\n\n# Topic\n', encoding="utf-8")
            errors, _, count = checker.validate(root)
            self.assertEqual(count, 2)
            self.assertEqual(errors, [])
            (root / "README.md").write_text("[Guide](docs/guide.md#missing)\n", encoding="utf-8")
            errors, _, _ = checker.validate(root)
            self.assertTrue(any("missing section" in error for error in errors))

    def test_generated_documents_are_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Guide\n", encoding="utf-8")
            (root / "work").mkdir()
            (root / "work/generated.md").write_text("[bad](missing.md)\n", encoding="utf-8")
            errors, _, count = checker.validate(root)
            self.assertEqual((errors, count), ([], 1))

    def test_broken_and_unverified_http_are_distinct(self):
        for code, expected in ((404, "broken"), (403, "unverified"), (503, "unverified")):
            with self.subTest(code=code):
                with patch.object(checker, "urlopen", side_effect=HTTPError("https://example.invalid", code, "test", None, None)), patch.object(checker.time, "sleep"):
                    self.assertEqual(checker.check_http("https://example.invalid")[0], expected)


if __name__ == "__main__":
    unittest.main()
