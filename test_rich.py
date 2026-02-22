from rich.console import Console
from rich.markdown import Markdown, CodeBlock
from rich.syntax import Syntax

class MyCodeBlock(CodeBlock):
    def __rich_console__(self, console, options):
        code = str(self.text).rstrip()
        syntax = Syntax(code, self.lexer_name, line_numbers=True, word_wrap=True, theme="monokai")
        yield syntax

Markdown.elements["code_block"] = MyCodeBlock
Markdown.elements["fence"] = MyCodeBlock

console = Console(force_terminal=True, width=80)
text = """
# Test
This is **bold** and `code`.
```python
def hello():
    print("world")
```
"""

md = Markdown(text)
console.print(md)
