from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users



app = FastAPI()

Base.metadata.create_all(bind=engine)
# create everyhing from database.py file and models.py file to be able to 
# create a new database that has a new table called todos with all the columns
# that we have specified in the models.py file

@app.get("/healthy")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)