from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import plotly.graph_objs as go
import os


app = FastAPI(dbug=True) # run server with: uvicorn server:app --reload

UPLOAD_DIR = "uploads"

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get('/')
async def index():
    return {"message":"Hello, this is the base endpoint of the API."}

@app.post('/upload')
async def upload_files(files: list[UploadFile] = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_names =[]
    # file_paths = []
    if len(files) > 0:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            # file_paths.append(file_path)
            file_names.append(file.filename)
    else:
        return JSONResponse(content="No submitted files found")
    return JSONResponse(content={"message":"Files uploaded successfully", "File names":file_names})

@app.get('/files')
async def list_files():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

@app.get('/files/{file_name}')
async def read_file(file_name: str):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Example of reading the first 10 words from a text file
    if file_name.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            content = " ".join(file.readline().split()[:10])
    # Example of reading the first 3 rows from an Excel file
    elif file_name.endswith(".xlsx"):
        import pandas as pd
        try:
            df = pd.read_excel(file_path)
            content = df.head(3).to_dict()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        content = "Unsupported file type"
    
    return {"file_name": file_name, "content": content}

@app.get('/graph')
async def send_graph():
    # Example data
    x_values = [1, 2, 3, 4, 5]
    y_values = [10, 20, 30, 40, 50]
    graph_data = go.Scatter(x=x_values, y=y_values, mode='lines')
    graph_layout = go.Layout(title='Sample Graph', xaxis=dict(title='X-axis'), yaxis=dict(title='Y-axis'))
    fig = go.Figure(data=[graph_data], layout=graph_layout)

    graph_json = fig.to_json()
    return JSONResponse(content=graph_json)

@app.delete('/files/all')
async def delete_files():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    for file_name in os.listdir(UPLOAD_DIR):
        full_path = os.path.join(UPLOAD_DIR, file_name)
        if os.path.isfile(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            delete_files(full_path) #remove the files inside the inner directory
            os.rmdir(full_path)