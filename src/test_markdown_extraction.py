import unittest

from textnode import extract_markdown_images, extract_markdown_links


class TestMarkdownExtraction(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png")], matches
        )

    def test_multiple_images(self):
        text = (
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) "
            "and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertEqual(extract_markdown_images(text), [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
        ])

    def test_extract_markdown_links(self):
        text = "This is a link [to boot dev](https://www.boot.dev)"
        self.assertEqual(
            extract_markdown_links(text), [("to boot dev", "https://www.boot.dev")]
        )

    def test_multiple_links(self):
        text = (
            "This is text with a link [to boot dev](https://www.boot.dev) "
            "and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertEqual(extract_markdown_links(text), [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev"),
        ])

    def test_mixed_images_and_links(self):
        text = "![image](image.png) [site](https://example.com) ![other](other.jpg)"
        self.assertEqual(
            extract_markdown_images(text), [("image", "image.png"), ("other", "other.jpg")]
        )
        self.assertEqual(extract_markdown_links(text), [("site", "https://example.com")])

    def test_images_are_not_links(self):
        self.assertEqual(extract_markdown_links("![image](image.png)"), [])

    def test_links_are_not_images(self):
        self.assertEqual(extract_markdown_images("[site](https://example.com)"), [])

    def test_no_matches(self):
        for text in ("", "Just plain text", "https://example.com"):
            with self.subTest(text=text):
                self.assertEqual(extract_markdown_images(text), [])
                self.assertEqual(extract_markdown_links(text), [])

    def test_empty_labels_and_urls(self):
        self.assertEqual(extract_markdown_images("![](image.png) ![alt]()"), [
            ("", "image.png"), ("alt", ""),
        ])
        self.assertEqual(extract_markdown_links("[](page.html) [label]()"), [
            ("", "page.html"), ("label", ""),
        ])

    def test_adjacent_and_repeated_matches(self):
        self.assertEqual(extract_markdown_images("![a](a.png)![a](a.png)"), [
            ("a", "a.png"), ("a", "a.png"),
        ])
        self.assertEqual(extract_markdown_links("[a](/a)[a](/a)"), [
            ("a", "/a"), ("a", "/a"),
        ])

    def test_urls_with_query_and_fragment(self):
        url = "https://example.com/file?q=hello&size=2#section"
        self.assertEqual(extract_markdown_images(f"![image]({url})"), [("image", url)])
        self.assertEqual(extract_markdown_links(f"[link]({url})"), [("link", url)])

    def test_incomplete_markdown(self):
        for text in ("![alt](image.png", "[link](page.html", "![alt]image.png", "[link] page.html"):
            with self.subTest(text=text):
                self.assertEqual(extract_markdown_images(text), [])
                self.assertEqual(extract_markdown_links(text), [])


if __name__ == "__main__":
    unittest.main()
