"""Small stdlib-only HTML tree reader for the preserved source captures."""
from html.parser import HTMLParser
import re

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

class Node:
    def __init__(self, tag='', attrs=None):
        self.tag, self.attrs, self.children = tag, dict(attrs or []), []
    def walk(self, tag=None, cls=None):
        for child in self.children:
            if isinstance(child, Node):
                if (tag is None or child.tag == tag) and (cls is None or cls in child.attrs.get('class', '').split()):
                    yield child
                yield from child.walk(tag, cls)
    def text(self):
        return re.sub(r'\s+', ' ', ' '.join(c.text() if isinstance(c, Node) else c for c in self.children)).strip()

class Tree(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node('root'); self.stack = [self.root]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs); self.stack[-1].children.append(n)
        if tag not in VOID: self.stack.append(n)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID: self.handle_endtag(tag)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]; break
    def handle_data(self, data): self.stack[-1].children.append(data)

def content_blocks(text):
    root = Tree(text).root
    content = next(root.walk(cls='entry-content'), None)
    if content is None: return []
    # Only editorial paragraphs/headings; never export scripts, forms or widgets.
    return [(n.tag, n.text()) for n in content.walk() if n.tag in {'p', 'h2', 'h3', 'h4', 'li'} and n.text() and n.text() not in {'Save', 'Share', 'Tweet'}]
