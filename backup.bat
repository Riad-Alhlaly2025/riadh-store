@echo off
REM Backup script for MyShop on Windows

REM Configuration
set BACKUP_DIR=C:\backups\myshop
set DATE=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DB_NAME=myshop
set DB_USER=myshopuser

REM Create backup directory if it doesn't exist
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Backup database (assuming PostgreSQL)
echo Backing up database...
pg_dump -U %DB_USER% -h localhost %DB_NAME% > "%BACKUP_DIR%\myshop_db_%DATE%.sql"

REM Backup media files
echo Backing up media files...
tar -czf "%BACKUP_DIR%\myshop_media_%DATE%.tar.gz" media/

REM Backup logs
echo Backing up logs...
tar -czf "%BACKUP_DIR%\myshop_logs_%DATE%.tar.gz" logs/

echo Backup completed: %BACKUP_DIR%\myshop_%DATE%
pause