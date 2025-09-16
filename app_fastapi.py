from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd

app = FastAPI(title="Pricing Calculator")

# Serve your HTML template
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html") as f:
        return HTMLResponse(f.read())

# Your bulk upload endpoint
@app.post("/bulk_upload")
async def bulk_upload(file: UploadFile = File(...)):
    # Your existing processing logic here
    # But with async/await for better performance
    pass