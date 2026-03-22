from pygments.lexer import RegexLexer, include, default
from pygments.token import Text, Comment, Operator, Keyword, Name, String, Number

__all__ = ['LaTeXLexer']

class LaTeXLexer(RegexLexer):
    """
    Lexer for the TeX and LaTeX typesetting languages.
    """

    name = 'LaTeX'
    aliases = ['customlatex']
    filenames = ['*.tex', '*.aux', '*.toc']
    mimetypes = ['text/x-tex', 'text/x-latex']
    url = 'https://tug.org'
    version_added = ''

    tokens = {
        'general': [
            (r'%.*?\n', Comment),
            (r'[{}]', Name.Builtin),
            (r'[&_^]', Name.Builtin),
        ],
        'root': [
            (r'\\\[', String.Backtick, 'displaymath'),
            (r'\\\(', String, 'inlinemath'),
            (r'\$\$', String.Backtick, 'displaymath'),
            (r'\$', String, 'inlinemath'),
            (r'\\([a-zA-Z@_:]+|\S?)', Keyword, 'command'),
            (r'\\$', Keyword),
            include('general'),
            (r'[^\\$%&_^{}]+', Text),
        ],
        'math': [
            (r'\\([a-zA-Z]+|\S?)', Operator.Math),
            (r'[&_^\+\-\*/]', String),
            include('general'),
            (r'[0-9]+', Number),
            (r'[-=!+*/()\[\]]', Operator),
            (r'[^=!+*/()\[\]\\$%&_^{}0-9-]+', Name.Builtin),
            (r'[.*]', String),
        ],
        'inlinemath': [
            (r'\\\)', String, '#pop'),
            (r'\$', String, '#pop'),
            include('math'),
        ],
        'displaymath': [
            (r'\\\]', String, '#pop'),
            (r'\$\$', String, '#pop'),
            (r'\$', Name.Builtin),
            include('math'),
        ],
        'command': [
            (r'\[.*?\]', Name.Attribute),
            (r'\*', Keyword),
            default('#pop'),
        ],
    }

    def analyse_text(text):
        for start in ("\\documentclass", "\\input", "\\documentstyle",
                      "\\relax"):
            if text[:len(start)] == start:
                return True