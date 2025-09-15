from fastapi import FastAPI
import uvicorn
from api.search import leslies_search, pool360_product_pull, leslies_product_pull, pool360_search

app = FastAPI()


@app.get("/product/pool360")
async def pool360_product(product_name: str) -> dict:
    product = await pool360_product_pull(product_name)
    return product

@app.get("/search/leslies")
async def search_leslie(product_name: str) -> dict:
    products = await leslies_search(product_name)
    return products

@app.get("/product/leslies/{product_id}")
async def pool360_product(product_id: str) -> dict:
    product = await leslies_product_pull(product_id)
    return product

@app.get("/autocomplete")
async def autocomplete(query: str) -> dict:
    products = await pool360_search(query)
    return products


if __name__ == "__main__":
    uvicorn.run(
        "main:app",      # points to the file (main.py) and app instance
        host="localhost",
        port=8000,
        reload=True
    )