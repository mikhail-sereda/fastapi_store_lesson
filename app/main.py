from fastapi import FastAPI

from app.routers import categories, products

app = FastAPI(
    title="Fastapi Интернет магазин проба пера.",
    version="0.1.0",
)

app.include_router(
    categories.router,
)
app.include_router(
    products.router,
)


# Корневой эндпоинт для проверки
@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}
