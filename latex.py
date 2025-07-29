from typing import Iterable

from database import database_exercices

class latex_document():
    def __init__(self, db: database_exercices, filename: str, numberwithin: str = "") -> None:
        self.db = db
        self.flnm = filename
        self.content = gen_header(numberwithin)
    def add_toc(self) -> None:
        self.content += "\n\\tableofcontents"
    def add_sec(self, name: str) -> None:
        self.content += f"\n\\section{{{name}}}"
    def add_ssec(self, name: str) -> None:
        self.content += f"\n\\subsection{{{name}}}"
    def add_exercises(self, exs: list[int], showdiff: bool = True, showid: bool = True, showans: bool = True, showfullinfo: bool = False, showreq: bool = False, currchap: str = "") -> None:
        self.content += gen_exercises(self.db, map(self.db.get_exercise, exs), len(str(self.db.max_exercises())), showdiff, showid, showans, "\n\\vspace{5pt}\n%", showfullinfo, showreq, currchap)
    def add_exercise(self, ex: int, showdiff: bool = True, showid: bool = True, showans: bool = True, showfullinfo: bool = False, showreq: bool = False, currchap: str = "") -> None:
        self.content += gen_exercises(self.db, [self.db.get_exercise(ex)], len(str(self.db.max_exercises())), showdiff, showid, showans, "\n\\vspace{5pt}\n%", showfullinfo, showreq, currchap)
    def jump_page(self) -> None:
        self.content += "\n\\null\\newpage%"
    def gen_doc(self) -> None:
        content = self.content + gen_end()
        file = open(self.flnm, "w", encoding="utf-8")
        file.write(content)
        file.close()
        

def generate_latex(db: database_exercices, ex_list: Iterable[tuple[int, str, int, str, str, str, str, str]], max_exr_len: int, filename: str, showdiff: bool = True, showid: bool = True, showans: bool = True, numberwithin: str = "") -> None:
    content = gen_header(numberwithin)
    content += gen_exercises(db, ex_list, max_exr_len, showdiff, showid, showans, "\n\\vspace{5pt}\n%")
    content += gen_end()
    file = open(filename, "w", encoding="utf-8")
    file.write(content)
    file.close()

def gen_header(numberwithin: str = "") -> str:
    return """
        \\documentclass[11pt]{altarticle}
        \\toggleanalysepar\\togglebornelimits
        \\usepackage{marginnote}
        \\marginparsep=10pt
        \\marginparwidth=2cm
        \\createtheorem{exercice}{Exercice}{exo}{exercice}{""" + numberwithin + """}{true}
        \\makeatletter
        \\newenvironment{corrige}[2][]%
            {%
                \\par%
                \\altarticle@comparestring{#1}{}%
                    {\\def\\argI{\\textbf{\\boldmath Corrigé (\\textsl{\\thmref{#2}})~:}}}%
                    {\\def\\argI{\\textbf{\\boldmath Corrigé (\\textsl{\\thmref{#2}}#1)~:}}}%
                \\begin{leftbartitle}{\\argI}%
                    \\def\\footnotetext{\\savefootnote}%
                    \\small%
                    \\setlength{\\belowdisplayskip}{0pt}\\setlength{\\belowdisplayshortskip}{0pt}\\setlength{\\abovedisplayskip}{0pt}\\setlength{\\abovedisplayshortskip}{0pt}%
                    \\let\\textitemize\\itemize%
                    \\let\\itemize\\prvitemize%
            }{%
                \\end{leftbartitle}%
            }%
        \\makeatother
        \\def\\beginhard{\\begingroup\\color{red!75!black}}
        \\def\\endhard{\\endgroup}
        \\def\\classique{\\color{blue!62.5!black}}
        \\allowdisplaybreaks
        \\setlist[enumerate]{topsep=0pt,nosep,label=\\itemnb{\\arabic*},beginpenalty=10000}
        \\usepackage{bbmt}
        \\begin{document}
    """

def gen_end() -> str:
    return "\n\\end{document}"

def diff_string(diff: int) -> str:
    if diff < 0:
        return '{\\classique\\Large\\filledstar' + str(diff + 6) + "}"
    else:
        return '\\Large\\filledstar' + str(diff)

def gen_exercises(db: database_exercices, ex_list: Iterable[tuple[int, str, int, str, str, str, str, str]], max_exr_len: int, showdiff: bool = True, showid: bool = True, showans: bool = True, ex_sep: str = "", showfullinfo: bool = False, showreq: bool = False, currchap: str = "") -> str:
    content = ""
    first = True
    for (_id, name, diff, exr, ans, year, req_chap, chap) in ex_list:
        if not first:
            content += ex_sep
        content += f"\n\\exercice[{_id}-{currchap}][][][true]{{{name}}}\\marginnote{{{f'\\texttt{{[{str(_id).zfill(max_exr_len)}]}}' if showid else ''}}}{{\\reversemarginpar\\marginnote{{{diff_string(diff) if showdiff else ''}}}}}\\emph{{{(', '.join(map(lambda x: db.get_chapter(int(x)).lower(), (filter(lambda x: x != '' and x != currchap, req_chap.split(',')))))) if showreq else ""}}}\\par\\nobreak%"
        req_chap_str = ', '.join(map(lambda x: db.get_chapter(int(x)), (filter(lambda x, chap=currchap: x != '' and x != chap, req_chap.split(',')))))
        if showfullinfo:
            content += f"\n\\begingroup\\slshape Année(s): {', '.join(map(lambda x: db.get_year(int(x)), (filter(lambda x: x != '', year.split(',')))))}\\\\Chapitre(s): {', '.join(map(lambda x: db.get_chapter(int(x)), (filter(lambda x: x != '', chap.split(',')))))} {('\\\\Chapitre(s) nécessaire(s): ' + req_chap_str) if req_chap_str else ''}\\endgroup%\n"
        content += f"\n{exr}%"
        if showans:
            content += f"""%
                \\vspace{{2.5pt}}
                \\begin{{corrige}}{{exo {_id}-{currchap}}}
                    \\toggleanalysedisplay\\togglebigopdisplay\\togglelimlimits\\togglebornelimits%
                    {ans if ans != "" else "À venir\\dots"}
                \\end{{corrige}}
            %"""
        first = False
    return content


def generate_exercise_sheet(ex_list_1: Iterable[tuple[int, str, int, str, str, str, str, str]], ex_list_2: Iterable[tuple[int, str, int, str, str, str, str, str]], ex_list_3: Iterable[tuple[int, str, int, str, str, str, str, str]], max_exr_len: int, filename: str, showminipagemars: bool = False) -> None:
    file = open(filename, "w", encoding="utf-8")
    content = """
        \\documentclass[a4paper,11pt,geometryargs={textheight=856.375pt,left=2.5cm,right=2.5cm}]{altarticle}
        \\renewcommand{\\label}[1]{\\relax}
        \\marginparsep=10pt
        \\marginparwidth=2cm
        \\pagenumbering{gobble}
        \\parindent=0pt
        \\setlength{\\voffset}{5.5655pt}
        \\setlength{\\headheight}{0pt}
        \\toggleanalysepar\\toggleanalysedisplay\\togglebigopdisplay\\togglebigoplimits\\togglelimlimits
        \\createtheorem{exercice}{Exercice}{exo}{exercice}{section}{true}
        \\renewcommand{\\theexercice}{\\arabic{exercice}}
        \\usepackage{marginnote}
        \\usepackage{bbmt}
        \\def\\beginhard{}
        \\def\\endhard{}
        \\usepackage{xparse}
        \\makeatletter
        \\ExplSyntaxOn
        \\NewDocumentCommand{\\hideit}{}
        {
        \\gaweiliex_hide:
        }
        \\NewDocumentCommand{\\hideitems}{}
        {
        \\bool_set_true:N \\l_gaweiliex_hide_bool
        }
        \\NewDocumentCommand{\\showitems}{}
        {
        \\bool_set_false:N \\l_gaweiliex_hide_bool
        }
        \\bool_new:N \\l_gaweiliex_hide_bool
        \\cs_new_protected:Nn \\gaweiliex_hide:
        {
        \\bool_if:NT \\l_gaweiliex_hide_bool
        {
            \\stepcounter{\\@enumctr}%
            \\item[]\\vspace{-\\baselineskip}%
            \\peek_regex_replace_once:nn
            % search \\item followed by anything until finding
            % \\item or \\hideit or \\end{<current environment>}
            { \\c{item}.*?(\\c{item}|\\c{hideit}|\\c{end}\\{\\u{@currenvir}\\}) }
            % replace by the matching item
            { \\1 }
        }
        }
        \\ExplSyntaxOff
        \\makeatother
        \\hideitems
    """
    content += f"""
        \\begin{{document}}{{\\color{{lightgray}}\\hrule}}\\vfill{'\\hrule' if showminipagemars else ''}\\stepcounter{{section}}\\begin{{minipage}}[t][8.5cm][t]{{\\textwidth}}%
    """
    for (_id, name, _, exr, _, _, _, _) in ex_list_1:
        content += f"\n\\exercice[{_id}][][][true]{{{name}}}\\marginnote{{\\texttt{{[{str(_id).zfill(max_exr_len)}]}}}}\\par\\nobreak%"
        content += f"\n{exr}%"
        content += "\n\\vspace{2.5pt}\n%"
    content += f"""
        \\end{{minipage}}{'\\hrule' if showminipagemars else ''}\\vfill{{\\color{{lightgray}}\\hrule}}\\vfill{'\\hrule' if showminipagemars else ''}\\stepcounter{{section}}%
        \\begin{{minipage}}[t][8.5cm][t]{{\\textwidth}}%
    """
    for (_id, name, _, exr, _, _, _, _) in ex_list_2:
        content += f"\n\\exercice[{_id}][][][true]{{{name}}}\\marginnote{{\\texttt{{[{str(_id).zfill(max_exr_len)}]}}}}\\par\\nobreak%"
        content += f"\n{exr}%"
        content += "\n\\vspace{2.5pt}\n%"
    content += f"""
        \\end{{minipage}}{'\\hrule' if showminipagemars else ''}\\vfill{{\\color{{lightgray}}\\hrule}}\\vfill{'\\hrule' if showminipagemars else ''}\\stepcounter{{section}}%
        \\begin{{minipage}}[t][8.5cm][t]{{\\textwidth}}%
    """
    for (_id, name, _, exr, _, _, _, _) in ex_list_3:
        content += f"\n\\exercice[{_id}][][][true]{{{name}}}\\marginnote{{\\texttt{{[{str(_id).zfill(max_exr_len)}]}}}}\\par\\nobreak%"
        content += f"\n{exr}%"
        content += "\n\\vspace{2.5pt}\n%"
    content += f"""
        \\end{{minipage}}{'\\hrule' if showminipagemars else ''}
        \\vfill{{\\color{{lightgray}}\\hrule}}
    """
    content += "\n\\end{document}"
    file.write(content)
    file.close()

def gen_book(db: database_exercices, flnm: str, numberwithin: str = "subsection", showans: bool = False) -> None:
    doc = latex_document(db, flnm, numberwithin)
    doc.add_toc()
    for y_id, yname in [("", "Non répertorié"),("2","MPS/2I"),("1","MP(I)")]: # À modifier, garder l'ordre
        y = False
        for c_id, cname in [("", "Non répertorié")] + sorted(db.list_chapters(), key=lambda x: x[1]):
            c = False
            for x in map(lambda x: x[0], db.list_exercises(f" year LIKE '%,{y_id},%' AND chapters LIKE '%,{c_id},%' ORDER BY difficulty")):
                if not y:
                    doc.jump_page()
                    doc.add_sec(yname)
                    y = True
                if not c:
                    doc.add_ssec(cname)
                    c = True
                doc.add_exercise(x, showans=showans, showreq=True, currchap = str(c_id))
    doc.gen_doc()