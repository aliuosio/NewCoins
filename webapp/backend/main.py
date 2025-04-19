from fastapi import FastAPI
from analysed_coins import router as analysed_coins_router
from indicators import router as indicators_router

app = FastAPI()
app.include_router(analysed_coins_router)
app.include_router(indicators_router)

@app.get("/api/health")
def health():
    return {"status": "ok"}
