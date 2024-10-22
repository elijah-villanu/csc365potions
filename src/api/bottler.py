from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


    


router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """

    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    # Each bottle has a quantity of what proportion of red, blue, and
    # Expressed in integers from 1 to 100 that must sum up to 100.
    

    with db.engine.begin() as connection:

        bottle_plan = []

        # ml = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory WHERE id = 1"))
        # for row in ml:


        r_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar()
        r_stock = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar()
        g_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        g_stock = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        b_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar()
        b_stock = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar()
        
        r_made, g_made, b_made, d_made, v_made, b_made = 0, 0, 0, 0, 0, 0
    #Checks if there is enough in barrel, then bottles it
    #Use modulus floor
        while r_ml >= 100:
            r_made += 1
            r_stock += 1
            r_ml = r_ml - 100

        while g_ml >= 100:
            g_made += 1
            g_stock += 1
            g_ml = g_ml - 100
        
        while b_ml >= 100:
            b_made += 1
            b_stock += 1
            b_ml = b_ml - 100

        #When updating potion quantity, make sure adding, not overiding
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions = '{r_stock}', num_red_ml = '{r_ml}' WHERE id = 1"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = '{g_stock}', num_green_ml = '{g_ml}' WHERE id = 1"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_potions = '{b_stock}', num_blue_ml = '{b_ml}' WHERE id = 1"))            
    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": r_made
            },
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": g_made
            },
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": b_made
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())