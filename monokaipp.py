from pygments.style import Style
from pygments.token import Token, Comment, Keyword, Name, String, Error, Number, Operator, Generic, Whitespace, Literal, Punctuation

class MonokaiPlusPlusStyle(Style):
    background_color = "#2D2A2E"
    default_style = ""

    styles = {
        Token:              "#FCFCFA",
        Whitespace:         "#727072",
        Comment:            "italic #7970A9",
        Comment.Hashbang:   "italic #A9DC76",
        Comment.Multiline:  "italic #A9DC76",
        Comment.Preproc:    "#AB9DF2",
        Comment.Single:     "italic #A9DC76",
        Comment.Special:    "italic #A9DC76",
        Keyword:            "bold #FF6188",
        Keyword.Constant:   "#AB9DF2",
        Keyword.Declaration:"#FF6188",
        Keyword.Namespace:  "#FF6188",
        Keyword.Pseudo:     "#FC9867",
        Keyword.Reserved:   "#FF6188",
        Keyword.Type:       "#A9DC76",
        Operator:           "#FF6188",
        Operator.Word:      "bold #FF6188",
        Operator.Math:      "#66d9ef",
        Name:               "#FCFCFA",
        Name.Attribute:     "#FFD866",
        Name.Builtin:       "#AB9DF2",
        Name.Builtin.Pseudo:"#FC9867",
        Name.Class:         "bold #A9DC76",
        Name.Constant:      "#AB9DF2",
        Name.Decorator:     "#FF6188",
        Name.Entity:        "#FCFCFA",
        Name.Exception:     "#FF6188",
        Name.Function:      "bold #FFD866",
        Name.Label:         "#FC9867",
        Name.Namespace:     "#FCFCFA",
        Name.Tag:           "#FF6188",
        Name.Variable:      "#FCFCFA",
        String:             "#A9DC76",
        String.Backtick:    "#A9DC76",
        String.Char:        "#A9DC76",
        String.Doc:         "italic #A9DC76",
        String.Double:      "#A9DC76",
        String.Escape:      "#FFD866",
        String.Heredoc:     "#A9DC76",
        String.Interpol:    "#FC9867",
        String.Other:       "#A9DC76",
        String.Regex:       "#FFD866",
        String.Single:      "#A9DC76",
        String.Symbol:      "#A9DC76",
        Number:             "#AB9DF2",
        Generic.Deleted:    "#FF6188",
        Generic.Emph:       "italic",
        Generic.Error:      "#FF6188",
        Generic.Heading:    "bold #FCFCFA",
        Generic.Inserted:   "#A9DC76",
        Generic.Output:     "#727072",
        Generic.Prompt:     "#727072",
        Generic.Strong:     "bold",
        Generic.Subheading: "bold #FCFCFA",
        Generic.Traceback:  "#FF6188",
        Error:              "#FF6188 bg:#1E0010",

        Literal:                   "#ae81ff", # class: 'l'
        Literal.Date:              "#e6db74", # class: 'ld'
        Punctuation:               "#f8f8f2" # class: 'p'
    }