@echo off
echo Starting FreeGPT4 server...
start "" /B cmd /C "cd gpt4_web_api\src && python -m FreeGPT4_Server"
echo Waiting for server to initialize...
timeout /t 5 >nul

echo Running dataset generation...
python dataset_gen.py

echo Shutting down server...
taskkill /IM python.exe /F >nul 2>&1

echo Done.
pause
