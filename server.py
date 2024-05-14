from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
#from fastapi.templating import Jinja2Templates
from starlette.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from xgboost import XGBClassifier
import plotly.graph_objs as go
import plotly.express as px
import os
import urllib


app = FastAPI(dbug=True) # run server with: uvicorn server:app --reload


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/plots", StaticFiles(directory="plots"), name="plots")

UPLOAD_DIR = "uploads/" # /
PLOT_DIR = "shap_plots/"

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
async def home(request:Request):
    '''Показывает домашнюю страницу'''
    about = "Добро пожаловать!"
    return templates.TemplateResponse("index.html", { #index
        "request":request,
        "header":"Выберите действие:",
        "message":about
        })

@app.get('/uploadfiles')
async def show_upload(request: Request):
    '''Открывает страницу для загрузки файлов'''
    return templates.TemplateResponse("upload/index.html",{ #upload.html
        "request":request,
        "header":"Загрузка файлов",
        "message":"Выберите файлы и нажмите отправить"
    })

@app.post('/upload')
async def upload_files(request:Request, files: list[UploadFile] = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_names =[]
    # file_paths = []
    for file in files:
        if file.filename == "":
            return templates.TemplateResponse("index.html",{
                "request":request,
                "message":"Вы не выберали файлы, попробуйте еще раз."
            })
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        # print(len(files))
        # print(file)
        # print(file.filename)
        # print(file_path)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        # file_paths.append(file_path)
        file_names.append(file.filename)
    return templates.TemplateResponse("index.html",{
        "request":request,
        "header":f"Файлы {file_names} загружены!"
    })

def read_patient(path):
    '''Возвращает первого пациента из excel файла'''
    excel_path = 'Stones_Train.xlsx'
    try:
        df = pd.read_excel(path)
        df = df.fillna(value=0)
        df = df.drop(['MESTOZIT'], axis=1)
        X = df.drop(['X-RAY'], axis=1)[:1]
        return X
    except ValueError:
        return pd.DataFrame()
    except KeyError:
        return pd.DataFrame()
    except:
        return pd.DataFrame()


def predict(file_name):
        '''Возвращает предсказание модели по данным пациента из файла'''
        X = read_patient(file_name)
        if X.empty:
            return "Ошибка формата файла! Пожалуйста, проверьте файл."
        loaded_model = XGBClassifier()
        loaded_model.load_model('xgb_model.json')
        try:
            prediction = loaded_model.predict_proba(X)
        except:
            return "Ошибка работы модели. Убедитесь, что файл соответсвует требованиям."
        is_sick = loaded_model.predict(X)[0]
        prob = prediction[0][1]
        if is_sick:
            result = f"Пациент предрасположен к МКБ. Уверенность модели = {prob:.0%}"
        else:
            prob = 1 - prob
            result = f"Пациент не предрасположен к МКБ. Уверенность модели = {prob:.0%}"
        return result

@app.post('/uploadpatient')
async def upload_patient_file(request:Request, files: list[UploadFile] = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_names =[]
    for file in files:
        if file.filename == "":
            return templates.TemplateResponse("index.html",{
                "request":request,
                "header":"Загрузка файлов",
                "message":"Выберите файлы и нажмите отправить"
            })
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        file_names.append(file.filename)
        patient_prediction = predict(file_path)
    return templates.TemplateResponse("index.html",{
        "request":request,
        "header":"Файл пациента загружен.",
        "message":patient_prediction
    })

@app.get('/files')
async def list_files(request:Request):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    files = os.listdir(UPLOAD_DIR)
    msg ="default msg"
    if len(files) > 0:
        msg = ""
    else:
        msg="Загруженных файлов не найдено"
    return templates.TemplateResponse("files/index.html",{
        "request":request,
        "header":"Загруженные файлы",
        "message":msg,
        "files": files
        })

@app.get('/deletefiles')
async def delete_files(request:Request):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    for file_name in os.listdir(UPLOAD_DIR):
        full_path = os.path.join(UPLOAD_DIR, file_name)
        if os.path.isfile(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            delete_files(full_path) #remove the files inside the inner directory
            os.rmdir(full_path)
    return templates.TemplateResponse("index.html", { #redirect('/')
        "request":request,
        "header":"Выберите действие:",
        "message":"Файлы удалены."
        })

@app.get('/graph')
async def show_graph(request:Request):
    plots = []
    descriptions = []
    plots.append('Figure_1.png')
    plot = 'Figure_1.png'
    description ='График SHAT-метрики'
    return templates.TemplateResponse("graph/index.html", {
        "request":request,
        'header':'График влияния факторов',
        'plot':plot,
        'description':description
    })

# @app.get('/files/{file_name}')
# async def read_file(file_name: str):
#     os.makedirs(UPLOAD_DIR, exist_ok=True)
#     file_path = os.path.join(UPLOAD_DIR, file_name)
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not found")
    
#     # Example of reading the first 10 words from a text file
#     if file_name.endswith(".txt"):
#         with open(file_path, "r", encoding="utf-8") as file:
#             content = " ".join(file.readline().split()[:10])
#     # Example of reading the first 3 rows from an Excel file
#     elif file_name.endswith(".xlsx"):
#         try:
#             df = pd.read_excel(file_path)
#             content = df.head(3).to_dict()
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=str(e))
#     else:
#         content = "Unsupported file type"
    
#     return {"file_name": file_name, "content": content}
