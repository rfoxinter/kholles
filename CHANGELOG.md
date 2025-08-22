# Version history
## 202208221500
- Fix exercise range selection in export to PDF
- Disable <samp>Escape</samp> key on <samp>QDialog</samp>
- Add warning for exercises with uncomplete corrected version
- Replace “1” by an empty value when selecting an exercise to edit
- Prevent additional LaTeX compilation when the first contains an error
- Add table with the distribution of exercises in export to PDF
- Display database compression on save popup and after exiting
## 202508112030
- Fix error code when uploading a file other than <samp>exercices.db.zip</samp> to pCloud
- Fix cursor not showing as pointer on some buttons
- Fix sorting diacritics
- Fix exercise sheet generation for students 2 and 3
- Fix the Python HTTP server
- Add warnings when generating exercise sheets with answers when an exercise has no corrected version
- Add save database option in main menu
## 202508091330
- Fix duplicate exercises <samp>id</samp>s in different years in LaTeX
- Make the database download use a static code
- Make the Python HTTP server for visualisation available
- Add exercise selection and difficulty option in export to PDF
## 202508071110
- Fix exercise sheet generation for students 2 and 3
- Imports restricted to required functions and classes
- Added debug mode
- Sort years and chapters in manager
- Change database compression format
- Hide scrollbars
- Add export and import feature
- Use the pCloud API to store the database and generated PDF files
- Use the pCloud API to fetch the database
## 202508031900
- Fix stars font not applying in <samp>posix</samp> systems
- Workaround for stars displaying with only one colour in the difficulty dropdown on <samp>posix</samp> systems by changing the background
- Change working directory when compiling LaTeX
- Add edit chapters and years feature
- Add version badge
## 202507300830
- Fix error when no database exists by creating a new empty one
- Fix error using <samp>windll</samp> on <samp>posix</samp> systems
- Fix error using the <samp>MonokaiPlusPlusStyle</samp> style in <samp>CodeSyntaxHighlight</samp>
- Add VERSIONS file
## 202507291540
- First release
- Create README contaning the Python dependencies and required files and licenses
