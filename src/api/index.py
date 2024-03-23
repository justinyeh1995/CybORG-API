from typing import List, Dict, Union

from fastapi import FastAPI, Depends
from pydantic import BaseModel

# @To-Do import CyborgAAS...

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
