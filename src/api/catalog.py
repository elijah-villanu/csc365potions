from fastapi import APIRouter
import sqlalchemy
from src import database as db


router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        gs_result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        green_stock = int(gs_result.fetchone()[0])
        rs_result = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        red_stock = int(rs_result.fetchone()[0])
        bs_result = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))
        blue_stock = int(bs_result.fetchone()[0])

    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": green_stock,
                "price": 50,
                "potion_type": [0, 100, 0, 0],
            },
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": red_stock,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            },
            {
                "sku": "BLUE_POTION_0",
                "name": "blue potion",
                "quantity": blue_stock,
                "price": 50,
                "potion_type": [0, 0, 100, 0],
            }
        ]
