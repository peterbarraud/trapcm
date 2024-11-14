ECHO off

SET phpport=8089
SET startdir=the.dr.nefario.backside
SET phpdir=the.dr.nefario.backside\php.min

ECHO Running PHP on PORT %phpport%

%phpdir%\php -S localhost:%phpport% -t %startdir% -c %phpdir%\php.ini || (
	pause
)
