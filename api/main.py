from fastapi import FastAPI
import asyncio
from api.search import leslies_search, pool360_search, pwp_search, heritage_search
from api.search import pool360_product_pull, leslies_product_pull, pwp_product_pull, heritage_product_pull
import uvicorn
app = FastAPI()


@app.get("/search/items")
async def search_items(query: str) -> dict:
    pool360_task = pool360_search(query=query)
    leslies_task = leslies_search(query=query)
    pwp_task = pwp_search(query=query)
    heritage_task = heritage_search(query=query)

    pool360_products, leslies_products, pwp_products, heritage_products = await asyncio.gather(
        pool360_task, leslies_task, pwp_task, heritage_task
    )
    full_list = {
        "pool360": pool360_products | {"site" : "Pool360"},
        "leslies": leslies_products | {"site" : "Leslie's"},
        "pool_water_products": pwp_products | {"site" : "Pool Water Products"},
        "heritage": heritage_products | {"site" : "Heritage"},
    }
    return full_list

@app.get("/product")
async def pool360_product(site: str, product_id: str) -> dict:
    if site == "pool360":
        product = await pool360_product_pull(product_id=product_id)
    elif site == "leslies":
        product = await leslies_product_pull(product_id=product_id)
    elif site == "pool_water_products":
        product = await pwp_product_pull(product_id=product_id)
    elif site == "heritage":
        product = await heritage_product_pull(product_id=product_id)
    return product


if __name__ == "__main__":
    uvicorn.run(
        "main:app",      # points to the file (main.py) and app instance
        host="localhost",
        port=8000,
        reload=True
    )