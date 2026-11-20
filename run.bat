@echo off
title BuildForge Enterprise CI/CD Pipeline
echo ======================================================================
echo           Starting BuildForge Enterprise Pipeline & Delivery
echo ======================================================================
echo.

echo [1/3] Building and starting Docker containers...
docker compose up -d --build

echo.
echo [2/3] Waiting for Nginx reverse proxy and App to become healthy...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Opening BuildForge Dashboard in your default browser...
start http://localhost:8090

echo.
echo ======================================================================
echo BuildForge is running at: http://localhost:8090
echo To run automated tests: python test_pipeline.py
echo To view logs: docker compose logs -f
echo To stop: docker compose down
echo ======================================================================
pause
