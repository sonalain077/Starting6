@echo off
cd /d "C:\Users\phams\Desktop\ProjetFullstack\backend"
python -m uvicorn app.main:app --reload --port 8000
