ECHO off

set username=%1
set password=%2
set database=%3

mariadb.min\bin\mysql -u %username% -p%password% -D %database%