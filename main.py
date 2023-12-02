from fastapi import FastAPI,Request,Depends,Form,UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi import status
from sqlalchemy.orm import Session
from sql_app.database import SessionLocal,engine
from models import Users
import models
import pandas as pd

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/', response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    users_data = db.query(models.Users).all()
    return templates.TemplateResponse("index.html",{"request": request,"users_data":users_data})

@app.post('/upload/')
async def create_file(request: Request, file: UploadFile = Form(...),db: Session = Depends(get_db)):
    url = app.url_path_for("home")
    print(file,'daxoooo')
    try:
        df = pd.read_csv(file.file)
        for index, row in df.iterrows():
            users_data = models.Users(name=row['name'], age=row['age'])
            db.add(users_data)
        db.commit()
        return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
    except:
        return RedirectResponse(url=url, status_code=status.HTTP_400_BAD_REQUEST)
