import unittest
from core.downloader import clean_title

class DownloaderHelperTests(unittest.TestCase):
    def test_removes_windows_invalid_filename_characters(self):
        self.assertEqual(clean_title('a:b/c*?'), 'a_b_c__')

    def test_empty_title_has_fallback(self):
        self.assertEqual(clean_title("   "), "download")

if __name__ == "__main__":
    unittest.main()
