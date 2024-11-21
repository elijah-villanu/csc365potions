from fastapi import APIRouter
import sqlalchemy
from src import database as db


router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    catalog = []
    with db.engine.begin() as connection:
        potions_query = """
                        SELECT p.potion_sku, p.name, COALESCE(SUM(pl.quantity), 0) AS quantity,
                            p.price, p.red_ml, p.green_ml, p.blue_ml, p.dark_ml 
                        FROM potions AS p
                        LEFT JOIN potion_ledger AS pl
                            ON pl.item_sku = p.potion_sku
                        GROUP BY p.potion_sku,p.name, p.price, p.red_ml, p.green_ml, p.blue_ml, p.dark_ml
                        """
        potions = connection.execute(sqlalchemy.text(potions_query))
        
        for row in potions:
            if row.quantity > 0:
                rbgd_array = [row.red_ml, row.green_ml, row.blue_ml, row.dark_ml]
                catalog.append({
                    "sku": row.potion_sku,
                    "name": row.name,
                    "quantity": row.quantity,
                    "price": row.price,
                    "potion_type": rbgd_array,
                })

    return catalog
