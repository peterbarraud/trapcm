ECHO off

IF EXIST mdb.running (
	ECHO The DB seems to be running. Please check
	pause
) ELSE (
	ECHO Creating the mdb.running file that is used by this script to see if the MariaDB server is running.
	ECHO Do NOT delete the mdb.running file manually. That is deleted by 
	ECHO MariaDB running > mdb.running
	ECHO Do NOT close this using Ctrl+C. Close it by running (double-click) 
	the.dr.nefario.backside\mariadb.min\bin\mysqld || (
		pause
	)
)
