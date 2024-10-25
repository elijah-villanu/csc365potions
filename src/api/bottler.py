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
        bottles_made = {
            "red":0,
            "green":0,
            "blue":0,
            "dark":0,
            "brown":0,
            "violet":0
        }
        potions_table = connection.execute(sqlalchemy.text("SELECT name, quantity FROM potions"))
        potions = {row.name: row.quantity for row in potions_table}
        ml_table = connection.execute(sqlalchemy.text("SELECT type, ml FROM barrels"))
        ml = {row.type: row.ml for row in ml_table}
        
        for key_ml in ml:
            value = ml[key_ml]
            print(f"{key_ml} {value}")
            made = 0
            potion_type = [0,0,0,0]
            made_any = False
            while value >= 100:
                if "red" in key_ml:
                    made += 1
                    value -=100
                    potions["red potion"] += 1
                    potion_type = [100,0,0,0]
                    made_any = True
                if "green" in key_ml:
                    made += 1
                    value -=100
                    potion_type = [0,100,0,0]
                    potions["green potion"] += 1
                    made_any = True
                if "blue" in key_ml:
                    made += 1
                    value -=100   
                    potion_type = [0,0,100,0]
                    potions["blue potion"] += 1
                    made_any = True
                else:
                    break
            
            if made_any:
                bottle_plan.append({
                    "potion_type": potion_type,
                    "quantity": made
                })
        potion_query = f"""
                    UPDATE potions
                    SET quantity = CASE
                        WHEN id = 1 THEN {potions["red potion"]}
                        WHEN id = 2 THEN {potions["green potion"]}
                        WHEN id = 3 THEN {potions["blue potion"]}
                        ELSE quantity
                    END
                    WHERE id IN (1,2,3)
                    """
        connection.execute(sqlalchemy.text(potion_query))


    print(bottle_plan)
    return bottle_plan             

if __name__ == "__main__":
    print(get_bottle_plan())