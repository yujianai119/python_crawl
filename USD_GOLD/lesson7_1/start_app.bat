@echo off
cd /d "d:\Github\python_crawl\lesson7_1"
"d:\Github\python_crawl\.venv\Scripts\streamlit.exe" run streamlit_app.py --server.port 8501 --logger.level error
pause
