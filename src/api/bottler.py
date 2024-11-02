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
    """
    Runs after bottler plan and uses list of PotionInventory made by the bottler plan
    """
    
    potion_query = f"""
                    UPDATE potions
                    SET quantity = CASE
                    """
    potions_table_query = """
                    SELECT * 
                    FROM potions
                    """
    with db.engine.begin() as conn:
        potions_table = conn.execute(sqlalchemy.text(potions_table_query))
        quantity = {row.type:row.quantity for row in potions_table}

        
        for potion in potions_delivered:
            type_string = str(potion.potion_type)
            quantity[type_string] += potion.quantity
            
        print(f"Current Quantity: {quantity}")
        
        for potion in quantity:
            potion_to_add = f"WHEN type = '{potion}' THEN {quantity[potion]} "
            potion_query += potion_to_add #String concat 
        potion_query += "end"
        conn.execute(sqlalchemy.text(potion_query))    
            
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
        potion_query = """
                        SELECT name, quantity,red_ml,blue_ml, green_ml, dark_ml
                        FROM potions
                       """
        potions_table = connection.execute(sqlalchemy.text(potion_query))
        
        ml_table = connection.execute(sqlalchemy.text("SELECT type, ml FROM barrels"))
        ml = {row.type: row.ml for row in ml_table}

        for potion in potions_table:
            if potion.red_ml <= ml["red"] and potion.blue_ml <= ml["blue"] and potion.green_ml <= ml["green"] and potion.dark_ml <= ml["dark"]:
                bottle_plan.append({
                    "potion_type": [potion.red_ml,potion.blue_ml,potion.green_ml,potion.dark_ml],
                    "quantity": 1
                })


    print(f"Bottle plan:{bottle_plan}")
    return bottle_plan             

if __name__ == "__main__":
    print(get_bottle_plan())
