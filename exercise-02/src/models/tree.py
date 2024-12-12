class TreeNode:
    def __init__(self, name: str, properties: dict):
        self.name = name
        self.children: list[TreeNode] = []
        self.properties = []
        self.max_width = len(name)

        for key, value in properties.items():
            display_value = f"{key}: {value}"
            self.max_width = max(len(display_value), self.max_width)

            self.properties.append(display_value)

        self.max_height = 1 + len(self.properties) # For the two edges of the bax and the text

    def get_height(self):
        return self.max_height + 4 # For the two edges and padding of the bax and the text
    
    def get_width(self):
        return self.max_width + 4 # For the two edges and padding of the bax and the text

    def render(self, indentation_length: int = 0):

        body: str = ""

        root = self.__render_box(indentation_length)
        body = self.__render_children(indentation_length)

        return "\n".join([root, body])

    def __render_box(self, indentation_length: int = 0) -> str:
        indent = " " * indentation_length
        width = self.get_width()
        height = self.get_height()

        top = f"┌{'─' * width}┐" # Already indented for us
        title = f"{indent}│{self.name.center(width)}│"
        middle = "\n".join([f"{indent}│ {prop.ljust(width-1)}│" for prop in self.properties])
        bottom = f"{indent}└{'─' * width}┘"

        return "\n".join([top, title, middle, bottom])
    
    def __render_children(self, indentation_length) -> str:

        if len(self.children) == 0:
            return ""

        indent = " " * indentation_length
        branch = f"{indent}├──"
        last_branch = f"{indent}└──"
        new_indent_length = indentation_length + 3
        
        childs = self.children[:-1]
        last_child = self.children[-1]

        top = "\n".join([f"{branch}{child.render(new_indent_length)}" for child in childs])
        bottom = f"{last_branch}{last_child.render(new_indent_length)}"

        return f"{top}\n{bottom}"