from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from routers import reduce

app = FastAPI()


# Gắn thư mục static
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", 'r', encoding='utf-8') as f:
        return f.read()

# Nối router
app.include_router(reduce.router)












