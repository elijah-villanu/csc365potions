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

        # bottle_plan = []
        # bottles_made = {
        #     "red":0,
        #     "green":0,
        #     "blue":0,
        #     "dark":0,
        #     "brown":0,
        #     "violet":0
        # }
        # potions_table = connection.execute(sqlalchemy.text("SELECT potion_sku, quantity FROM potions"))
        # potions = {row.potion_sku: row.quantity for row in potions_table}
        # print(potions)
        # ml_table = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"))
        # ml = dict([row._asdict() for row in ml_table])
        # print(type(ml))
        # for key in ml:
        #     print(key)
            # value = ml[type]
            # made = 0
            # while value >= 100:
            #     if "red" in type and potions["red"] > 0:
            #         made += 1
            #         value -=100
            # bottle_plan.append({
            #     "potion_type": [100, 0, 0, 0],
            #     "quantity": made
            # })

        # print(bottle_plan)
        # return bottle_plan     





        
        
    #     ml_inventory = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"))
    #     for ml in ml_inventory:
            

                 
        r_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar()
        r_stock = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id = 1")).scalar()
        g_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        g_stock = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id = 2")).scalar()
        b_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar()
        b_stock = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id = 3")).scalar()



        
        
        r_made, g_made, b_made = 0, 0, 0
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
        potion_query = f"""
                UPDATE potions
                SET quantity = CASE
                    WHEN id = 1 THEN {r_stock}
                    WHEN id = 2 THEN {g_stock}
                    WHEN id = 3 THEN {b_stock}
                    ELSE quantity
                END
                WHERE id IN (1,2,3)
                """
        connection.execute(sqlalchemy.text(potion_query))

        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = '{r_ml}' WHERE id = 1"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = '{g_ml}' WHERE id = 1"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml = '{b_ml}' WHERE id = 1"))    
        # print (bottle_plan)        
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