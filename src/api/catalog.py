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
                            p.price, p.rgbd 
                        FROM potions AS p
                        LEFT JOIN potion_ledger AS pl
                            ON pl.item_sku = p.potion_sku
                        GROUP BY p.potion_sku,p.name, p.rgbd, p.price
                        """
        potions = connection.execute(sqlalchemy.text(potions_query))
        
        for row in potions:
            catalog.append({
                "sku": row.potion_sku,
                "name": row.name,
                "quantity": row.quantity,
                "price": row.price,
                "potion_type": row.rgbd,
            })

    return catalog
