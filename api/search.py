import os
from dotenv import load_dotenv
import aiohttp
import urllib.parse
import re
from typing import Any, Optional
from lxml import html as LH
import json

load_dotenv()

LESLIE_STORES = [541, 367, 1507]
LESLIES_SEARCH = "https://core.dxpapi.com/api/v1/core/?q={query}&auth_key=kkde0gmtwbup2bjq&account_id=6704&domain_key=lesliespool&request_id=794601000621&_br_uid_2=uid%253D9629816895277%253Av%253D15.0%253Ats%253D1724938009534%253Ahc%253D809&url=https%253A%252F%252Fpegasus.lesliespool.com%252Fon%252Fdemandware.static%252FSites-lpm_site-Site%252F-%252Fen_US%252Fv1728455837586%252Fon%252Fdemandware.store%252FSites-lpm_site-Site&ref_url=&request_type=search&fl=pid%2Curl%2Cdescription%2Ctitle%2Cthumb_image%2Cbrand%2Cprice%2Csale_price&start=0&facet.field=isDeliveryEligible&search_type=keyword&rows=25&facet=true&client_id=a233c1f2-f115-434d-959e-efc789d0cd45"
LESLIES_PRODUCT_INFO = "https://lesliespool.com/s/lpm_site/dw/shop/v20_4/products/{product_id}?all_images=False&expand=images%2Cprices%2Cvariations%2Cavailability%2Cpromotions%2Coptions&sid={store_id}&postalCode=75077-7239&client_id=a233c1f2-f115-434d-959e-efc789d0cd45"

POOL360_SEARCH = "https://www.pool360.com/api/v2/products?includeSuggestions=true&search={query}"
POOL360_INVENTORY = "https://www.pool360.com/api/v1/realtimeinventory?expand=warehouses"
POOL360_PRICING = "https://www.pool360.com/api/v1/realtimepricing"
POOL360_PRODUCT_INFO = "https://www.pool360.com/api/v2/products?productIds={product_id}"

PWP_USER = os.getenv("PWP_USER")
PWP_PASSWORD = os.getenv("PWP_PASSWORD")
PWP_LOGIN = "https://poolwaterproducts.com/storefrontCommerce/login.do"
PWP_SEARCH = "https://poolwaterproducts.com/storefrontCommerce/search.do?searchType=keyword&keyword={query}&numResults=50"
PWP_PRODUCT_INFO = "https://poolwaterproducts.com/storefrontCommerce/itemDetail.do?itm_id={product_id}&itm_index=0&orderQty=1"
PWP_COOKIE = ...
FULL_PWP_COOKIE = f"accountId=5591; shoppingCart=""; JSESSIONID={SESSION_ID}; __utma=190507434.2125184611.1758548975.1758548975.1758548975.1; __utmb=190507434.4.10.1758548975; __utmz=190507434.1758548975.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; __utmc=190507434"
PWP_PLACEHOLDER = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSBlPTXRyZ5WF65z-rgpEPay1KnanxpJFD-BQ&s"

HERITAGE_COOKIE = os.getenv("HERITAGE_COOKIE")
HERITAGE_SEARCH = "https://www.heritagepoolplus.com/rest/V1/productIndex/mine/klevusearch"
HERITAGE_PRICING = "https://www.heritagepoolplus.com/rest/V1/srsdistribution/mine/getproductprice"
HERITAGE_PRODUCT_INFO = "https://www.heritagepoolplus.com/rest/V1/productIndex/mine/details"
HERITAGE_BASE_URL = "https://www.heritagepoolplus.com/"
HERITAGE_INVENTORY = "https://www.heritagepoolplus.com/rest/V1/srsdistribution/mine/getinventoryallbranch"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15"

POOL360_COOKIE = os.getenv("POOL360_COOKIE")

BASIC_HEADERS = {"User-Agent": USER_AGENT}
POOL360_HEADERS = {"User-Agent": USER_AGENT, "Cookie": POOL360_COOKIE, "Origin": "https://www.pool360.com"}
HERITAGE_HEADERS = {"User-Agent": USER_AGENT} | {"Cookie": HERITAGE_COOKIE, "x-requested-with": "XMLHttpRequest"}

async def pool360_search(query: str) -> dict:
    query = urllib.parse.quote(query)
    session = aiohttp.ClientSession()

    response = await session.get(POOL360_SEARCH.format(query=query), headers=POOL360_HEADERS)
    response = await response.json()
    products = response["products"]

    product_ids = [{
        "productId": p["id"],
        "unitOfMeasure": p["unitOfMeasures"][0]["unitOfMeasure"],
        "qtyOrdered": 1
    } for p in products]

    response = await session.post(POOL360_PRICING, headers=POOL360_HEADERS, json={"productPriceParameters": product_ids})
    product_pricing = await response.json()
    product_pricing = product_pricing["realTimePricingResults"]
    pricing_mapping = {}
    for pricing in product_pricing:
        pricing_mapping[pricing["productId"]] = pricing["unitListPriceDisplay"]

    new_products = []
    for product in products:
        new_products.append({
            "pid": product["id"],
            "title": product["productTitle"],
            "url": "https://pool360.com/" + product["canonicalUrl"],
            "price": pricing_mapping[product["id"]],
            "brand": product["brand"]["name"],
            "description": product["properties"]["shortDescription"],
            "thumb_image": product["mediumImagePath"]
        })
    await session.close()
    return {"items": new_products[:15]}


async def pool360_product_pull(product_id: str) -> dict:
    product_id = urllib.parse.quote(product_id)
    session = aiohttp.ClientSession()

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
    product_pricing = await response.json()
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


async def leslies_search(query: str) -> dict:
    query = urllib.parse.quote(query)
    session = aiohttp.ClientSession()
    response = await session.get(LESLIES_SEARCH.format(query=query), headers=BASIC_HEADERS)
    search_results = await response.json()
    search_results = search_results["response"]["docs"]
    for result in search_results:
        result["price"] = f"${result['price']}"

    await session.close()
    return {"items" : search_results}


async def leslies_product_pull(product_id: str) -> dict:
    session = aiohttp.ClientSession()

    product_info =  ...
    stock = []
    for store_id in LESLIE_STORES:
        response = await session.get(LESLIES_PRODUCT_INFO.format(product_id=product_id, store_id=store_id), headers=BASIC_HEADERS)
        product_info = await response.json()
        stock.append(
                {"location": product_info["c_availability"]["store"]["name"],
                 "qty": product_info["c_availability"]["location_availability"]["quantity"]}
        )
    full_data = {
        "id": product_id,
        "name": product_info["name"],
        "description": product_info.get("short_description", "No Description"),
        "product_number": product_info.get("manufacturer_sku", "No SKU"),
        "url": f"https://lesliespool.com/{product_id}.html",
        "price": f"${product_info["price"]}",
        "unit_of_measure": "Item",
        "stock": stock,
        "site": "Leslie's",
        "images": [product_info["image_groups"][0]["images"][0]["link"]],
        "brand_name": product_info.get("brand", "No Brand"),
    }
    return full_data


async def pwp_login():
    session = aiohttp.ClientSession()
    form = aiohttp.formdata.FormData()
    form.add_field("usr_name", PWP_USER)
    form.add_field("usr_password", PWP_PASSWORD)
    form.add_field("nextForward", "home.do")
    await session.post(PWP_LOGIN, data=form)
    cookies = {c.key: c.value for c in session.cookie_jar}

    global PWP_COOKIE
    PWP_COOKIE = cookies["JSESSIONID"]
    await session.close()


async def pwp_search(query: str) -> dict:
    def extract_items(html_text: str) -> list[dict[str, Any]]:
        """
        Extract item entries from the given HTML.

        Returns a list of dicts with:
          - item_number (int)
          - name (str)                # from the following details row
          - price_raw (str)           # like "$5.29"
          - qty (int)                 # "30"
          - image (str)               # "/storefrontCommerce/images/noimagethumb.gif"
        """

        def _txt(x: Optional[str]) -> str:
            return (x or "").strip()

        ITEMNUM_FROM_NAME = re.compile(r'itemNumber(\d+)EACH', re.I)

        def _num(x: str) -> Optional[int]:
            x = (x or "").strip()
            return int(x) if x.isdigit() else None

        doc = LH.fromstring(html_text)
        items: list[dict[str, Any]] = []

        # product rows look like the first TR in your pair
        ROW_PRED = (
            'contains(concat(" ", normalize-space(@class), " "), " rowshaded ")'
            ' or '
            'contains(concat(" ", normalize-space(@class), " "), " rownotshaded ")'
        )

        product_rows = doc.xpath(f'//tr[{ROW_PRED}]')

        for tr in product_rows:
            # We only want rows that contain the hidden itemNumber…EACH input
            hidden_vals = tr.xpath(
                './/input[starts-with(translate(@name,"ITEMNUMBER","itemnumber"), "itemnumber")]/@value')
            if not hidden_vals:
                # not the top row—likely the description row
                continue

            # item number (prefer the hidden value; fallback to name attr)
            item_number = None
            for v in hidden_vals:
                try:
                    item_number = int(v)
                    break
                except (TypeError, ValueError):
                    pass
            if item_number is None:
                # fallback from the "name" attribute (e.g., itemNumber103719EACH)
                for name_attr in tr.xpath('.//input/@name'):
                    m = ITEMNUM_FROM_NAME.search(name_attr or "")
                    if m:
                        item_number = int(m.group(1))
                        break

            # columns: [1]=image, [2]=SKU link, [3]=qty, [4]=price, ...
            tds = tr.xpath('./td')
            qty_text = _txt(tds[2].text_content()) if len(tds) >= 3 else ""
            price_raw = _txt(tds[3].text_content()) if len(tds) >= 4 else ""
            img_srcs = tr.xpath('.//img/@src')
            image = f"https://poolwaterproducts.com/{img_srcs[0]}" if "noimagethumb" not in img_srcs[0] else PWP_PLACEHOLDER

            # pair with the *next* rownotshaded row for the long name/description
            name = ""
            nxt = tr.xpath(f'following-sibling::tr[{ROW_PRED}][1]')
            if nxt:
                tds2 = nxt[0].xpath('./td')
                if tds2:
                    name = _txt(tds2[0].text_content())

            items.append({
                "pid": item_number,
                "title": name,
                "url": PWP_PRODUCT_INFO.format(product_id=item_number),
                "price": price_raw,
                "brand": "",
                "description": "",
                "thumb_image": image,
            })

        return items

    await pwp_login()
    query = urllib.parse.quote(query)
    session = aiohttp.ClientSession()
    response = await session.get(PWP_SEARCH.format(query=query), headers=BASIC_HEADERS | {"Cookie": FULL_PWP_COOKIE.format(SESSION_ID=PWP_COOKIE)})
    response = await response.text()
    await session.close()
    ids = extract_items(response)
    return {"items": ids}


async def pwp_product_pull(product_id: str) -> dict:

    def parse_product(page_source: str, product_id: str):
        tree = LH.fromstring(page_source)

        # --- Product fields ---
        # name (the descriptive text under the item code)
        name = tree.xpath(
            "//form[@name='itemDetailForm']"
            "//td[@class='item']/parent::tr/following-sibling::tr[1]"
            "/td[@class='text']/text()"
        )
        name = name[0].strip() if name else ""

        # manufacturer item
        manufacturer_item = tree.xpath(
            "//td[@class='label'][normalize-space()='Manufacturer Item:']/following-sibling::td/text()")
        manufacturer_item = manufacturer_item[0].strip() if manufacturer_item else ""

        # price
        price = tree.xpath("//td[@class='label'][normalize-space()='Sell Price:']/following-sibling::td/text()")
        price = price[0].strip() if price else ""

        # qty avail (main)
        qty_avail = tree.xpath("//td[@class='label'][normalize-space()='Qty Avail']/following-sibling::td/text()")
        qty_avail = qty_avail[0].strip() if qty_avail else "0"

        # image url
        image_url = tree.xpath("//img[contains(@src,'/images/medium/')]/@src")
        image_url = f"https://poolwaterproducts.com/{image_url[0]}" if image_url else PWP_PLACEHOLDER

        # warehouses (extra table)
        warehouses = []
        for row in tree.xpath("//tr[@class='rownotshaded']"):
            cells = row.xpath("./td/text()")
            if len(cells) >= 4:
                if cells[0] != "RH":
                    continue
                location = cells[1].strip().split("-")[1]
                qty = cells[2].strip()
                warehouses.append({
                    "location": location,
                    "qty": int(qty) if qty.isdigit() else 0,
                })

        full_data = {
            "id": product_id,
            "name": name,
            "description": "No Description",
            "product_number": manufacturer_item,
            "url": PWP_PRODUCT_INFO.format(product_id=product_id),
            "price": price,
            "unit_of_measure": "Each",
            "stock": [
                {"location": "Dallas", "qty": int(qty_avail)},
                *warehouses
            ],
            "site": "Pool Water Products",
            "images": [image_url],
            "brand_name": "N/A"
        }

        return full_data
    await pwp_login()
    session = aiohttp.ClientSession()
    response = await session.get(
        PWP_PRODUCT_INFO.format(product_id=product_id),
        headers=BASIC_HEADERS | {"Cookie": FULL_PWP_COOKIE.format(SESSION_ID=PWP_COOKIE)}
    )
    response = await response.text()
    await session.close()
    return parse_product(response, product_id)


async def heritage_search(query: str) -> dict:
    session = aiohttp.ClientSession()

    body = {"params": {"store_id": "17", "search_term": query, "selected_slider_category": "", "p": 1, "page_count": 20, "promos_filter": []}}
    response = await session.post(HERITAGE_SEARCH, headers=HERITAGE_HEADERS, json=body)
    results = await response.json()
    results = json.loads(results).get("hits")

    pricing_request_map = {}
    for result in results.get("hits", []):
        item = result["_source"]
        pricing_request_map[item["part"]] = item["id"]

    pricing_body = {"productInfo": json.dumps({"products": pricing_request_map}, separators=(",", ":"))}
    response = await session.post(HERITAGE_PRICING, headers=HERITAGE_HEADERS, json=pricing_body)
    pricing_results = await response.json()
    pricing_results = json.loads(pricing_results)

    items = []
    for result in results.get("hits", []):
        item = result["_source"]
        price = pricing_results.get(item["id"])
        if not price:
            continue
        items.append({
            "pid": item["sku"],
            "title": item["name"],
            "url": item["product_url"],
            "price": f"${price["price"]}",
            "brand": item["brand"],
            "description": item["item_name"],
            "thumb_image": item["cloudinary_image_url"],
        })
    await session.close()
    return {"items": items}


async def heritage_product_pull(product_id: str) -> dict:
    session = aiohttp.ClientSession()

    product_body = {"params":{"sku":[product_id],"recent_view_skip":False}}
    response = await session.post(HERITAGE_PRODUCT_INFO, headers=HERITAGE_HEADERS, json=product_body)
    results = await response.json()
    product_info = results[0][0]


    inventory_body = {"productId": product_info["id"], "productUom": "EA"}
    response = await session.post(HERITAGE_INVENTORY, headers=HERITAGE_HEADERS, json=inventory_body)
    inventory_results = await response.json()
    inventory_results = json.loads(inventory_results)

    stock = []
    for result in inventory_results:
        stock.append({
            "location": result["branch"].replace("TEXAS POOL SUPPLY", "TPS"),
            "qty": int(result["stock_availability_text"].split(" ")[0]) if result["stock"] else 0,
        })
    pricing_body = {"productInfo" : json.dumps({"products": {product_info["part"]: product_info["id"]}}, separators=(",", ":"))}
    response = await session.post(HERITAGE_PRICING, headers=HERITAGE_HEADERS, json=pricing_body)
    pricing_results = await response.json()
    pricing_results = json.loads(pricing_results)

    full_data = {
        "id": product_id,
        "name": product_info["name"],
        "description": product_info["description"],
        "product_number": product_info["item_mfg_number"],
        "url": HERITAGE_BASE_URL + product_info["url_key"],
        "price": f"${pricing_results.get(product_info["id"])["price"]}",
        "unit_of_measure": "Each",
        "stock": stock,
        "site": "Heritage",
        "images": [product_info["cld_data"]["image"]],
        "brand_name": product_info["custom_attributes"][0].get("value", "N/A")
    }
    await session.close()
    return full_data


