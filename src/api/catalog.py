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
        potions = connection.execute(sqlalchemy.text("SELECT * FROM POTIONS")).fetchall()
        for row in potions:
            type = [row[8]]
            catalog.append({
                "sku": row[1],
                "name": row[2],
                "quantity": row[3],
                "price": row[4],
                "potion_type": type,
            })

    return catalog
