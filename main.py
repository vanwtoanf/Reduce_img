from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from routers import file_reduce, folder_reduce

app = FastAPI()


# Gắn thư mục static
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", 'r', encoding='utf-8') as f:
        return f.read()

# Nối router
app.include_router(file_reduce.file_router)
app.include_router(folder_reduce.folder_router)











