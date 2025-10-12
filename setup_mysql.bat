@echo off
echo ============================================================
echo CODEX MySQL Setup Helper
echo ============================================================
echo.
echo This will help you set up MySQL for CODEX
echo.
echo Step 1: Testing MySQL connection...
echo.

python test_mysql_connection.py

echo.
echo ============================================================
echo.
echo If connection was successful, press any key to continue setup...
echo If connection failed, fix the password issue first.
echo.
pause

echo.
echo Step 2: Running setup wizard...
echo.

python setup_mysql.py

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo To start your app: python app.py
echo To view users: python view_users.py
echo.
pause
