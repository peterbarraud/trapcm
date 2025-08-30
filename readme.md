# The TraPCM App
## Get started
1. Install VS Code
1. Install Python
1. Install Python Debugger extension for VSC
1. Point the Extension to your Python Compiler
On this computer, its here
`C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Python 3.13`
5. Run the following commands:
```
pip install flet
pip install Pillow
pip install opencv-python
pip install requests
pip install pywin32
pip install beautifulsoup4

```
6. Press Ctrl+F5

Should run fine

6. Create a folder for your QandA files
6. Put the folder (top-level) in this file
`add-q-and-a\libs\config.json` at `qandaFilesRoot`

The qanda folder structure is as follows:
`qandaFilesRoot/<source - jee or bits>/<exam_dir>/<subject>/`

Answer files:
`qandaFilesRoot/<source - jee or bits>/<exam_dir>/<subject>/answer-files`

Question files:
`qandaFilesRoot/<source - jee or bits>/<exam_dir>/<subject>/question-files`

Correct choices file location
`qandaFilesRoot/<source - jee or bits>/<exam_dir>/<subject>/<topic>/correct.choices`

## How to And QandA to TraPCM
### Download PDF and use iLovePDF
1. Download the PYQ PDF (mathongo is here: https://www.mathongo.com/iit-jee/jee-main-chapter-wise-questions-with-solutions)
1. Put the PDF here: `/trapcm/qanda-files/raw-data/mathongo/<subject>/<year>`
1. Use https://www.ilovepdf.com/ to covert the PDF to JPG files (one page for each file)
1. Create a folder, based on the exam inside the folder you created in step 2 above.
For example, for the April JEE exam, you can create a folder `apr`. Exact folder name is unimportant, just a convenient normenclature will help.
1. To make the names of the JPG files, use /trapcm/add-q-and-a/shorten-download-jpg-names.py

### How to make the QandA files
5. Run: `trapcm/makeqandafiles.bat`
* **env**: engg
* **source**: jee/bits/(any other exam)
* **subject**: `<subject>`
* **topic**: `<topic>`
* **exam**: this is the folder where the qanda files go - `/trapcm/qanda-files/source>/<the name the put in the exam field>`
This field is important, because this is where the UIApp picks the QandA from for each question.

*__Also, important: If the exam folder doesn't exist, we create it__*

6. Open `MS Paint`
1. Open the folder containing the JPG files created by ilovepdf - `Step 2` above
1. Also, open the PDF - the JPG file numbers are the same as the page Nos. on the PDF
1. Do the Make QandA file stuff

### How to create the correct choices file
(This is specific for mathongo, at least for now)

The correct.choices file, for each topic, is created in: `/trapcm/qanda-files/<source>/<the name in the exam field>/<subject>/<topic>/`

To create the file:
1. Go the downloaded mathongo PDF and copy all the Correct answers and put them into a file here: `/trapcm/qanda-files/<source>/<the name in the exam field>/<subject>/<topic>/all-choices.txt`
This is the format (Nothing that you need the )
```
Gravitation
1. (3) 2. (9) 3. (3) 4. (2) 5. (8) 6. (1) 7. (3)
```
2. Add this location here: `/trapcm/add-q-and-a/makecorrectchoicesfiles.py`
1. Run the script and, *hopefull*, you should have the correct answer files in each of the topic folders

Important: This script does *NOT* create any folder. So, if we don't find a folder, we'll just error out

### How to add the QandA to TraPCM
1. Run: `trapcm/uiapp.bat`
* **env**: engg
* **source**: jee/bits/(any other exam)
* **exam**: this is the folder where you put the QandA files. If you don't see an exam in the list, you didn't do the first part of creating the QandA files

`/trapcm/qanda-files/<source>/<the name in the exam field>`

Example: `/trapcm/qanda-files/<source>/2025-jan`
* **subject**: `<subject>`
* **topic**: `<topic>`
