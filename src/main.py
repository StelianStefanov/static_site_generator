from textnode import generate_pages_recursive
from copy_content import copy_contents

def main():
    copy_contents("static", "public")
    generate_pages_recursive("content", "template.html", "public")

main()