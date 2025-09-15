import os
from dotenv import load_dotenv
import aiohttp
import urllib.parse

load_dotenv()

LESLIES_SEARCH = "https://core.dxpapi.com/api/v1/core/?q={query}&auth_key=kkde0gmtwbup2bjq&account_id=6704&domain_key=lesliespool&request_id=794601000621&_br_uid_2=uid%253D9629816895277%253Av%253D15.0%253Ats%253D1724938009534%253Ahc%253D809&url=https%253A%252F%252Fpegasus.lesliespool.com%252Fon%252Fdemandware.static%252FSites-lpm_site-Site%252F-%252Fen_US%252Fv1728455837586%252Fon%252Fdemandware.store%252FSites-lpm_site-Site&ref_url=&request_type=search&fl=pid%2Curl%2Cdescription%2Ctitle%2Cthumb_image%2Cbrand%2Cprice%2Csale_price&start=0&facet.field=isDeliveryEligible&search_type=keyword&rows=10&facet=true&client_id=a233c1f2-f115-434d-959e-efc789d0cd45"
LESLIES_PRODUCT_INFO = "https://lesliespool.com/s/lpm_site/dw/shop/v20_4/products/{product_id}?all_images=False&expand=images%2Cprices%2Cvariations%2Cavailability%2Cpromotions%2Coptions&sid=541&postalCode=75077-7239&client_id=a233c1f2-f115-434d-959e-efc789d0cd45"

POOL360_SEARCH = "https://www.pool360.com/api/v1/autocomplete?query={query}"
POOL360_INVENTORY = "https://www.pool360.com/api/v1/realtimeinventory?expand=warehouses"
POOL360_PRICING = "https://www.pool360.com/api/v1/realtimepricing"
POOL360_PRODUCT_INFO = "https://www.pool360.com/api/v2/products?productIds={product_id}"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15"

POOL360_COOKIE = os.getenv("POOL360_COOKIE")

BASIC_HEADERS = {"User-Agent": USER_AGENT}
POOL360_HEADERS = {"User-Agent": USER_AGENT, "Cookie": POOL360_COOKIE, "Origin": "https://www.pool360.com"}

async def pool360_product_pull(product_name: str) -> dict:
    product_name = urllib.parse.quote(product_name)
    session = aiohttp.ClientSession()

    if product_name.count("-") >= 2:
        product_id = product_name
    else:
        response = await session.get(POOL360_SEARCH.format(query=product_name), headers=POOL360_HEADERS)
        response = await response.json()
        product_id = response["products"][0]["id"]

    response = await session.get(POOL360_PRODUCT_INFO.format(product_id=product_id), headers=POOL360_HEADERS)
    product_info = await response.json()
    product_info = product_info["products"][0]
    uom = product_info.get("unitOfMeasures", {})[0].get("unitOfMeasure")

    pricing_body = {"productPriceParameters": [
        {"productId": product_id,
         "unitOfMeasure": uom,
         "qtyOrdered": 1}
    ]}
    response = await session.post(POOL360_PRICING, headers=POOL360_HEADERS, json=pricing_body)
    product_pricing = None
    print(POOL360_PRICING, pricing_body)
    print("ISSUE", await response.text())
    print("ISSUE", await response.json())
    print("ISSUE", await response.read())


    product_pricing = product_pricing["realTimePricingResults"][0]

    response = await session.post(POOL360_INVENTORY, headers=POOL360_HEADERS, json={"productIds":[product_id]})
    product_inventory = await response.json()
    product_inventory = product_inventory["realTimeInventoryResults"][0]


    stock_data = []

    for warehouse in product_inventory["inventoryWarehousesDtos"][0]["warehouseDtos"]:
        message_type = warehouse["messageType"]
        if message_type == 1:
            stock_data.append({
                "location": warehouse["description"],
                "qty": warehouse["qty"],
            })

    full_data = {
        "id": product_id,
        "name": product_info["productTitle"],
        "description": product_info["properties"]["shortDescription"],
        "product_number": product_info["productNumber"],
        "url": "https://pool360.com/" + product_info["canonicalUrl"],
        "price": product_pricing["actualPriceDisplay"],
        "unit_of_measure": uom,
        "stock": stock_data,
        "site": "Pool 360",
        "images" : [product_info["largeImagePath"]],
        "brand_name": (product_info.get("brand") or {}).get("name", "No Brand"),
    }

    await session.close()
    return full_data

async def pool360_search(query: str) -> dict:
    product_name = urllib.parse.quote(query)
    session = aiohttp.ClientSession()

    response = await session.get(POOL360_SEARCH.format(query=product_name), headers=POOL360_HEADERS)
    response = await response.json()
    products = response["products"]
    await session.close()
    return {"items": products[:15]}

async def leslies_search(product_name: str) -> dict:
    product_name = urllib.parse.quote(product_name)
    session = aiohttp.ClientSession()
    response = await session.get(LESLIES_SEARCH.format(query=product_name), headers=BASIC_HEADERS)
    search_results = await response.json()
    search_results = search_results["response"]["docs"][:10]

    await session.close()

    return {"items" : search_results}


async def leslies_product_pull(product_id: str) -> dict:
    session = aiohttp.ClientSession()
    response = await session.get(LESLIES_PRODUCT_INFO.format(product_id=product_id), headers=BASIC_HEADERS)
    product_info = await response.json()

    full_data = {
        "id": product_id,
        "name": product_info["page_title"],
        "description": product_info.get("short_description", "No Description"),
        "product_number": product_info.get("manufacturer_sku", "No SKU"),
        "url": f"https://lesliespool.com/{product_id}.html",
        "price": f"${product_info["price"]}",
        "unit_of_measure": "Item",
        "stock": [
            {"location": product_info["c_availability"]["store"]["name"],
             "qty" : product_info["c_availability"]["location_availability"]["quantity"]}
        ],
        "site": "Leslie's",
        "images": [product_info["image_groups"][0]["images"][0]["link"]],
        "brand_name": product_info.get("brand", "No Brand"),
    }
    return full_data
