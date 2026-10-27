import os
import re
from enum import Enum
from typing import Any
from htmlnode import LeafNode, ParentNode


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, value):
        if not isinstance(value, TextNode):
            return NotImplemented

        return self.__dict__ == value.__dict__

    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"

def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if text_node.text_type == TextType.TEXT:
        return LeafNode(tag=None, value=text_node.text)

    if text_node.text_type == TextType.BOLD:
        return LeafNode(tag="b", value=text_node.text)

    if text_node.text_type == TextType.ITALIC:
        return LeafNode(tag="i", value=text_node.text)

    if text_node.text_type == TextType.CODE:
        return LeafNode(tag="code", value=text_node.text)

    if text_node.text_type == TextType.LINK:
        return LeafNode(tag="a", value=text_node.text, props={"href": text_node.url})

    if text_node.text_type == TextType.IMAGE:
        return LeafNode(tag="img", value="", props={"src": text_node.url, "alt": text_node.text})

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    
    for node in old_nodes:
        parts = re.split(r'(!\[[^\]]*\]\([^)]*\))', node.text)
        for txt in parts:
            matches = extract_markdown_images(txt)

            if not matches:
                if txt:  # Skip empty text parts
                    new_nodes.append(TextNode(txt, TextType.TEXT))
            else:
                alt, url = matches[0]
                new_nodes.append(TextNode(alt, TextType.IMAGE, url))

    return new_nodes

def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []

    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = re.split(r"(?<!!)(\[[^\[\]]*\]\([^()]*\))", node.text)
        for part in parts:
            if not part:
                continue

            matches = extract_markdown_links(part)
            if matches:
                label, url = matches[0]
                new_nodes.append(TextNode(label, TextType.LINK, url))
            else:
                new_nodes.append(TextNode(part, TextType.TEXT))
    return new_nodes


def split_nodes_delimiter(old_nodes: list[TextNode]) -> list[TextNode]:
    nodes = list(old_nodes)
    # Parse code first so its contents stay literal, and bold before single '*'.
    for delimiter, text_type in (
        ("`", TextType.CODE),
        ("**", TextType.BOLD),
        ("_", TextType.ITALIC),
        ("*", TextType.ITALIC),
    ):
        new_nodes = []
        for node in nodes:
            if node.text_type is not TextType.TEXT or delimiter not in node.text:
                new_nodes.append(node)
                continue

            parts = node.text.split(delimiter)
            if len(parts) % 2 == 0:
                raise ValueError(f"Unmatched Markdown delimiter: {delimiter}")

            for index, part in enumerate(parts):
                if part:
                    part_type = TextType.TEXT if index % 2 == 0 else text_type
                    new_nodes.append(TextNode(part, part_type))
        nodes = new_nodes

    return nodes


def text_to_textnodes(text) -> list[TextNode[Any, TextType]]:
    node = [TextNode(text, TextType.TEXT)]
    node = split_nodes_image(node)
    node = split_nodes_link(node)
    return split_nodes_delimiter(node)
    
def markdown_to_blocks(markdown) -> list:
    return [block.strip() for block in markdown.split("\n\n") if block.strip()]

def block_to_block_type(block) -> BlockType:
    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING

    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE

    lines = block.split("\n")

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    if all(line.startswith(f"{i + 1}. ") for i, line in enumerate(lines)):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(node) for node in text_nodes]


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.HEADING:
            level = len(block) - len(block.lstrip("#"))
            text = block[level + 1 :]
            children.append(ParentNode(f"h{level}", text_to_children(text)))

        elif block_type == BlockType.CODE:
            # Strip the opening ``` and closing ```
            code_text = block[3:-3].strip("\n")
            code_node = text_node_to_html_node(TextNode(code_text, TextType.TEXT))
            children.append(ParentNode("pre", [ParentNode("code", [code_node])]))

        elif block_type == BlockType.QUOTE:
            lines = block.split("\n")
            stripped = [line.lstrip(">").lstrip(" ") for line in lines]
            content = " ".join(stripped)
            children.append(ParentNode("blockquote", text_to_children(content)))

        elif block_type == BlockType.UNORDERED_LIST:
            lines = block.split("\n")
            items = []
            for line in lines:
                text = line[2:]  # strip "- "
                items.append(ParentNode("li", text_to_children(text)))
            children.append(ParentNode("ul", items))

        elif block_type == BlockType.ORDERED_LIST:
            lines = block.split("\n")
            items = []
            for line in lines:
                # Strip "N. " prefix
                text = re.sub(r"^\d+\.\s", "", line)
                items.append(ParentNode("li", text_to_children(text)))
            children.append(ParentNode("ol", items))

        else:
            # Paragraph — join lines with a space
            text = " ".join(block.split("\n"))
            children.append(ParentNode("p", text_to_children(text)))

    return ParentNode("div", children)


def extract_title(markdown):
    for line in markdown.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("No h1 header found")


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r") as f:
        markdown = f.read()

    with open(template_path, "r") as f:
        template = f.read()

    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    page = template.replace("{{ Title }}", title).replace("{{ Content }}", html)

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w") as f:
        f.write(page)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for item in os.listdir(dir_path_content):
        source_path = os.path.join(dir_path_content, item)
        if os.path.isfile(source_path) and item.endswith(".md"):
            dest_path = os.path.join(dest_dir_path, item.replace(".md", ".html"))
            generate_page(source_path, template_path, dest_path)
        elif os.path.isdir(source_path):
            generate_pages_recursive(source_path, template_path, os.path.join(dest_dir_path, item))


# node = TextNode("This is text with a *code block* word", TextType.TEXT)
# new_nodes = split_nodes_delimiter([node])
# node = TextNode(
#     "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
#     TextType.TEXT,
# )
# new_nodes = split_nodes_link([node])
# print(new_nodes)

#print(text_to_textnodes("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"))
print(markdown_to_blocks("""
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""))
