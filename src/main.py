import sys

from textnode import generate_pages_recursive
from copy_content import copy_contents

def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    copy_contents("static", "docs")
    generate_pages_recursive("content", "template.html", "docs", basepath)

main()