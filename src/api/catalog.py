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
    #     potions = connection.execute(sqlalchemy.text("SELECT * FROM POTIONS")).fetchall()
    #     for row in potions:
    #         connection.execute(sqlalchemy.text(""))

        green_stock = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        red_stock = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar()
        blue_stock = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar()
        
    # return catalog
    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": green_stock,
                "price": 10,
                "potion_type": [0, 100, 0, 0],
            },
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": red_stock,
                "price": 10,
                "potion_type": [100, 0, 0, 0],
            },
            {
                "sku": "BLUE_POTION_0",
                "name": "blue potion",
                "quantity": blue_stock,
                "price": 10,
                "potion_type": [0, 0, 100, 0],
            }
        ]
