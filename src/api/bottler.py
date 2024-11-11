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

    pot_ledger_query =  """
                                INSERT INTO potion_ledger
                                    (rgbd, quantity, item_sku)
                                VALUES 
                                    (:rgbd, :quantity, :item_sku) 
                        """
    potion_types_query =    """
                                SELECT rgbd, potion_sku, red_ml, green_ml, blue_ml, dark_ml
                                FROM potions  
                            """
    potions_added = []

    barrel_ledger_query =   """
                                INSERT INTO barrel_ledger
                                    (red_ml, green_ml, blue_ml, dark_ml, sku)
                                VALUES
                                    (:red_ml, :green_ml, :blue_ml, :dark_ml, :sku)
                            """
    ml_removed = []

    with db.engine.begin() as connection:
        
        potion_types_table = connection.execute(sqlalchemy.text(potion_types_query))
        potion_types = {}
        potion_ml = {}
        for row in potion_types_table:
            potion_ml[row.potion_sku] = [row.red_ml, row.green_ml, row.blue_ml, row.dark_ml]
            potion_types[row.rgbd] = row.potion_sku
        

        for potion in potions_delivered:
            rgbd = str(potion.potion_type)
            sku = potion_types[rgbd]
            potions_added.append({
                "rgbd": rgbd,
                "quantity": potion.quantity,
                "item_sku": sku
            })

            #potion_ml[] entry formatted as [r,g,b,d], so 0 = red etc.
            ml_removed.append({
                "red_ml": -potion_ml[sku][0],
                "green_ml": -potion_ml[sku][1],
                "blue_ml": -potion_ml[sku][2],
                "dark_ml": -potion_ml[sku][3],
                "sku": sku
            })

        # bulk insert potion_ledger
        connection.execute(sqlalchemy.text(pot_ledger_query),potions_added)
        connection.execute(sqlalchemy.text(barrel_ledger_query), ml_removed)
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    # Each bottle has a quantity of what proportion of red, blue, and
    # Expressed in integers from 1 to 100 that must sum up to 100. Base it all off ml!!!
    # Also update barrel ledger to subtract the ml used
    
    bottle_plan = []
    with db.engine.begin() as connection:
        potion_query = """
                        SELECT name, rgbd, red_ml, green_ml, blue_ml, dark_ml
                        FROM potions
                       """
        potions_table = connection.execute(sqlalchemy.text(potion_query))
        
        barrel_query = """
                    SELECT SUM(red_ml) AS red_ml,
                        SUM(green_ml) AS green_ml,
                        SUM(blue_ml) AS blue_ml,
                        SUM(dark_ml) AS dark_ml
                    FROM barrel_ledger
                 """
        ml_table = connection.execute(sqlalchemy.text(barrel_query)).fetchone()
        
        ml = {
            "red_ml": ml_table[0],
            "green_ml": ml_table[1],
            "blue_ml": ml_table[2],
            "dark_ml": ml_table[3]
        }

        for potion in potions_table:
            if(
                potion.red_ml <= ml["red_ml"]
                and potion.blue_ml <= ml["blue_ml"]
                and potion.green_ml <= ml["green_ml"]
                and potion.dark_ml <= ml["dark_ml"]
            ):
                # TRY QUANTITY = AND DIV BY NEEDED MODULUS DIV
                bottle_plan.append({
                    "potion_type": [potion.red_ml,potion.blue_ml,potion.green_ml,potion.dark_ml],
                    "quantity": 1
                })
                ml["red_ml"] -= potion.red_ml
                ml["blue_ml"] -= potion.blue_ml
                ml["green_ml"] -= potion.green_ml
                ml["dark_ml"] -= potion.dark_ml
                

    print(f"Bottle plan:{bottle_plan}")
    return bottle_plan             

if __name__ == "__main__":
    print(get_bottle_plan())
