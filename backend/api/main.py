from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(title="PSet 3 - Incident Management API")

# Incluimos tus rutas
app.include_router(router)

@app.get("/")
def home():
    return {"status": "online", "message": "Sistemas funcionando correctamente"}