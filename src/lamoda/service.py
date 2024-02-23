from typing import Dict
from bs4 import BeautifulSoup
from bson import ObjectId

from src.config import settings
from src.lamoda.repository import (
    insert_main_categories,
    insert_product_items,
    update_category_by_id,
)
from src.resources.kafka import producer_send_one
from src.lamoda.utils import get_html_text


MAIN_CATEGORIES_URL = [
    ("men", str(settings.LAMODA_URL_MEN_BREADCRUMB)),
    ("women", str(settings.LAMODA_URL_WOMEN_BREADCRUMB)),
    ("kids", str(settings.LAMODA_URL_KIDS_BREADCRUMB)),
]


async def parse_all_categories():
    """
    Function to parse main categories (men, women, kids).

    """
    parsed_data = []

    for category_name, url in MAIN_CATEGORIES_URL:
        parent_category_id = ObjectId()
        page = await get_html_text(url)
        soup = BeautifulSoup(page, "html.parser")

        category_divs = soup.find_all(
            "div", class_="x-tree-view-catalog-navigation__category"
        )

        subcategory_data = []
        for category in category_divs:
            elem = category.find("a", class_="x-link__label")
            if elem:
                name = elem.text.strip()
                link = elem["href"]
                slug = link.split("/")[-2]
                count = category.find(
                    "span", class_="x-tree-view-catalog-navigation__found"
                ).text.strip()

                subcategory_data.append(
                    {
                        "_id": ObjectId(),
                        "name": name,
                        "link": str(settings.LAMODA_URL_BASE) + link,
                        "amount": count,
                        "slug": slug,
                    }
                )

        parsed_data.append(
            {
                "_id": parent_category_id,
                "category": category_name,
                "link": url,
                "categories": subcategory_data,
            }
        )

    await insert_main_categories(parsed_data)

    for category in parsed_data:
        for subcategory in category["categories"]:
            await producer_send_one(parse_subcategory, subcategory)


async def parse_subcategory(data: dict):
    """
    Function to parse subcategory data.

    Parses main subcategory data and create task to parse full data of subcategory.
    """
    page = await get_html_text(data["link"])
    soup = BeautifulSoup(page, "html.parser")

    ul = soup.find("ul", class_="x-tree-view-catalog-navigation__subtree")

    subcategories = []
    for li in ul.find_all("li"):
        category = li.find("div", class_="x-tree-view-catalog-navigation__category")
        a = category.find("a", class_="x-link x-link__label")

        amount = category.find(
            "span", class_="x-tree-view-catalog-navigation__found"
        ).text.strip()
        name = a.text
        link = str(settings.LAMODA_URL_BASE) + a["href"]
        slug = link.split("/")[-2]

        subcategories.append(
            {
                "_id": ObjectId(),
                "name": name,
                "link": link,
                "amount": amount,
                "slug": slug,
            }
        )

    await update_category_by_id(data["_id"], "categories", subcategories)

    for subcategory in subcategories:
        await producer_send_one(parse_marketplace_items, subcategory)


async def parse_marketplace_items(subcategory: Dict):
    """
    Function to parse all products of specific subcategory.
    """
    base_link = subcategory["link"]

    paginator = 1
    while True:
        page = await get_html_text(base_link, page=paginator)
        soup = BeautifulSoup(page, "html.parser")
        products_divs = soup.find_all("div", class_="x-product-card__card")

        if not products_divs:
            break

        paginator += 1
        products = []

        for product in products_divs:
            data = {
                "_id": ObjectId(),
            }

            link = product.find(
                "a", class_="x-product-card__link x-product-card__hit-area"
            )
            if link:
                data["link"] = str(settings.LAMODA_URL_BASE) + link["href"]
                data["product_number"] = link["href"].split("/")[-3]

            product_name = product.find(
                "div", class_="x-product-card-description__product-name"
            )
            if product_name:
                data["product_name"] = product_name.text.strip()

            brand_name = product.find(
                "div", class_="x-product-card-description__brand-name"
            )
            if product_name:
                data["brand_name"] = brand_name.text.strip()

            single_price = product.find(
                "span", class_="x-product-card-description__price-single"
            )
            if single_price:
                data["single_price"] = single_price.text.strip().replace(" р.", "")

            new_price = product.find(
                "span", class_="x-product-card-description__price-new"
            )
            if new_price:
                data["new_price"] = new_price.text.strip().replace(" р.", "")

            old_price = product.find(
                "span", class_="x-product-card-description__price-old"
            )
            if old_price:
                data["old_price"] = old_price.text.strip().replace(" р.", "")

            image = product.find("img", class_="x-product-card__pic-img")
            if image:
                data["image"] = "https:" + image["src"]

            products.append(data)

        await insert_product_items(products, subcategory_id=subcategory["_id"])
