# Exercise manager
![Version Badge](https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fraw.githubusercontent.com%2Frfoxinter%2Fkholles%2Fmain%2FCHANGELOG.md&search=(%3F%3A%23%23%20)(%5B0-9%5D*)&replace=%241&label=Version&cacheSeconds=1)
## Installation
Python 3.10 or higher is required to run the exercise manager.  
The following Python libraries need to be installed to run the script:
- [Pygments](https://pypi.org/project/Pygments/)
- [PyQt6](https://pypi.org/project/PyQt6/)
- [PyQt6-WebEngine](https://pypi.org/project/PyQt6-WebEngine/)
- [superqt](https://pypi.org/project/superqt/)

A recent release of [PDF.js](https://github.com/mozilla/pdf.js) needs to be unzipped in the folder containing the <samp>\_\_init\_\_.py</samp> file.
## Usage
Run <samp>\_\_init\_\_.py</samp> to launch the exercise manager.  
The console contains the error messages as well as the LaTeX output when documents are compiled.  
The app needs to be closed via the main window and not via the console for the database to be saved. The database will not be saved automatically if the script is run in debug mode. The database can be saved manually with the button available in the app.  
For the LaTeX documents to compile, the <samp>texmf</samp> directory available at [https://github.com/rfoxinter/texmf](https://github.com/rfoxinter/texmf). Place the downloaded texmf folder in your local TeX tree or set the <samp>TEXMFHOME</samp> environment variable to point to it. A complete documentation is available at [https://wikibooks.org/wiki/LaTeX/Installing_Extra_Packages](https://wikibooks.org/wiki/LaTeX/Installing_Extra_Packages).  
The class used for the documents is the <samp>altarticle</samp> present in the above GitHub repository.

The script <samp>pcloud.py</samp> is provided to sync the database with [pCloud](https://www.pcloud.com/). The script is not an available option within the app and has to be run independently.  
Two options are available: <samp>--d</samp> to download the database (a backup is created as <samp>exercices_bkp.db.zip</samp>) and <samp>--u</samp> to upload files. If no files are given for the upload (as a comma-separated list: <samp>--u="file1,file2,file3"</samp>), only the database is uploaded. Paths should be specified relative to the directory from which the script is run. Running the script with no option will prompt a dialogue with the options presented above.  
For the script to run, three files need to be created: <samp>token.txt</samp> that contains the pCloud login token (available as the <samp>pcauth</samp> cookie on pCloud, only necessary for upload), <samp>db_folder.txt</samp> that contains the name of the folder to which the database needs to be uploaded (only necessary for upload) and <samp>db_token.txt</samp> that contains the id of the shared folder that contains the database (available after the <samp>?code=</samp> in the shared folder URL, only necessary for download).

When writing LaTeX code, somme commands are defined. <samp>\beginhard</samp> and <samp>\endhard</samp> allow to make some part of the exercise not available with the <samp>nohard</samp> or appear red when exercise sheets are generated. <samp>\indic{}</samp> allows to add a note in an exercise, that will not be generated in the exercise sheets.

When entering a list of exercises, the exercises need to be entered as a list separated by semi-colons and options for each exercise can be put between bracket, as a list and separated by comas. A range of exercises can be specified with <samp>-</samp> (bounds included).  
The available options are <samp>nohard</samp> (mentionned above) and specifying the questions to add on the exercise sheet (these numbers correspond to the index of the <samp>\item</samp> elements).  
For instance, to have question 4 of exercise 1 without the hard parts, questions 1 and 3 of exercise 2 and exercises 3 to 9, one can use <samp>1[4,nohard];2[1,3];3-9</samp>.  
The format for exercise sheets is <samp>{exercises for student 1};;{exercises for student 2};;{exercises for student 3};;;{bonus exercises}</samp>, where each <samp>{...}</samp> is of the above form.
## Licenses
This program is licensed under the GNU General Public License v3.0. 
See the [LICENSE](LICENSE.txt) file for details.

This product includes or requires software developed by third parties. The licences for these components are listed below. Full license texts for all dependencies are available in the <samp>legal</samp> folder.
- [PDF.js](https://github.com/mozilla/pdf.js) – licensed under the [Apache-2.0](https://raw.githubusercontent.com/mozilla/pdf.js/refs/heads/master/LICENSE)
- [pdfLaTeX](https://www.latex-project.org/) – licensed under the [LaTeX Project Public License v1.3c](https://www.latex-project.org/lppl/lppl-1-3c.txt)
- [Pygments](https://pygments.org/) – licensed under the [BSD-2-Clause](https://raw.githubusercontent.com/pygments/pygments/refs/heads/master/LICENSE)
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) – licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
- [PyQt6-WebEngine](https://www.riverbankcomputing.com/software/pyqtwebengine/) – licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
- [Python 3](https://www.python.org/) – licensed under the [Python Software Foundation License](https://docs.python.org/3/license.html#python-software-foundation-license-version-2)
- [SQLite](https://sqlite.org/) – released into the [public domain](https://sqlite.org/copyright.html)
- [superqt](https://github.com/pyapp-kit/superqt) – licensed under the [BSD-3-Clause](https://raw.githubusercontent.com/pyapp-kit/superqt/refs/heads/main/LICENSE)
- [Ubuntu font](https://design.ubuntu.com/font) – licensed under the [Ubuntu Font License v1.0](https://ubuntu.com/legal/font-licence)

THIS SOFTWARE IS PROVIDED "AS IS" AND WITHOUT ANY WARRANTIES, EXPRESS OR IMPLIED. THE DEVELOPERS AND CONTRIBUTORS EXPRESSLY DISCLAIM ALL WARRANTIES OF ANY KIND, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
