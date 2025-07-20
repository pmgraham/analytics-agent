import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware
from google.adk.cli.fast_api import get_fast_api_app
from app.agent import root_agent # Assuming root_agent is defined here

# Configure logging for google.adk
logging.basicConfig(level=logging.INFO) # Set to INFO or DEBUG for more verbosity
logging.getLogger("google.adk").setLevel(logging.INFO)

# Get the ADK FastAPI app, with the default web UI disabled
# This will be our main application
app: FastAPI = get_fast_api_app(
    agents_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"),
    session_service_uri=None, # Changed to use InMemorySessionService for local development
    allow_origins=["*"], # This is handled by CORSMiddleware below
    web=False # CRITICAL: Disables the default ADK UI
)

# Add CORS middleware directly to the ADK app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Allow requests from your React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the path to your React app's build directory
# Assuming your React app is in a 'frontend' folder and builds to 'frontend/dist'
frontend_build_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")

# Serve the static files of your React frontend
# This will serve index.html for any unmatched routes, effectively handling client-side routing
# IMPORTANT: This must come AFTER all API routes to ensure API calls are handled first.
app.mount("/", StaticFiles(directory=frontend_build_path, html=True), name="static")

# You can run this FastAPI app locally using:
# uvicorn main:app --reload --port 8000
# Or for production:
# gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080
