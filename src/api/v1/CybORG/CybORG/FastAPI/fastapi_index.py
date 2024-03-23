from typing import List, Dict, Union

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from CybORG import CybORG, CYBORG_VERSION 
# @To-Do import CyborgAAS...

app = FastAPI()

@app.get("/")
def read_root():
    print("Hello FastAPI")
    return {"Hello": "World"}


