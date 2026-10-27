class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        result = ""
        
        if not self.props:
            return result

        for key, value in self.props.items():
            if result == "":
                result = f'{key}="{value}"'
            else:
                result += f' {key}="{value}"'

        return result

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag=tag,
            value=value,
            children=None,
            props=props
        )

    def to_html(self):
        if self.value is None:
            raise ValueError("All leaf nodes must have a value")

        if self.tag is None:
            return self.value

        props = ""
        if self.props:
            props = " " + self.props_to_html()
        return f"<{self.tag}{props}>{self.value}</{self.tag}>"


    def __repr__(self):
        super().__repr__()
        return f"HTMLNode({self.tag}, {self.value}, {self.props})"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, value=None, children=children, props=props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("ParentNode must have a tag")

        if self.children is None:
            raise ValueError("All parent nodes must have a children")

        children_html = ""
        for child in self.children:
            children_html += child.to_html()

        return f"<{self.tag}>{children_html}</{self.tag}>"


test = HTMLNode(props={
    "href": "https://www.google.com",
    "target": "_blank",
})

print(test.props_to_html())
