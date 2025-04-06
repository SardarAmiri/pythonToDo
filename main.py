from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos, admin, users



app = FastAPI()

models.Base.metadata.create_all(bind=engine)
# create everyhing from database.py file and models.py file to be able to 
# create a new database that has a new table called todos with all the columns
# that we have specified in the models.py file

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)