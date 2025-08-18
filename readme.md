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
