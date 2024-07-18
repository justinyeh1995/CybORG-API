from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Union
from pprint import pprint

from api.v1.FastAPI import models
from api.v1.FastAPI.database import engine
from api.v1.FastAPI.api.main import api_router

# Create all tables
models.Base.metadata.create_all(bind=engine)

# Start main app
app = FastAPI()

# CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins (or use ["*"] for all)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include Routers
app.include_router(api_router, prefix="/api")

# Will be deprecated soon
@app.get("/", response_class=HTMLResponse)
def read_root():
    print("Hello FastAPI")
    return """
            "Hello FastAPI"
            """