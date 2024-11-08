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
                                    (rgbd, 
                                    quantity, 
                                    item_sku)
                                VALUES 
                                    (:rgbd,
                                    :quantity,
                                    :item_sku) 
                        """
    potion_types_query =    """
                                SELECT rgbd,
                                    potion_sku
                                FROM potions  
                            """
    potions_added = []
    
    # ledgerize bottler: rgbd, (+)quantity, item_sku (no cart_id/cart_item_id means its added)
    # Ledgerize purchase: rgbd, profit, (-)quantity, cart_id, cart_item_id !!! Do in checkout
    # Update barrels ledger with negative values to subtract

    with db.engine.begin() as connection:
        
        potion_types_table = connection.execute(sqlalchemy.text(potion_types_query))
        potion_types = {row.rgbd: row.potion_sku for row in potion_types_table}

        for potion in potions_delivered:
            type_string = str(potion.potion_type)
            sku = potion_types[type_string]
            potions_added.append({
                "rgbd": type_string,
                "quantity": potion.quantity,
                "item_sku": sku
            })

        # bulk insert potion_ledger
        connection.execute(sqlalchemy.text(pot_ledger_query),potions_added)
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
                        SELECT name, rgbd, red_ml, green_ml, blue_ml
                        FROM potions
                       """
        potions_table = connection.execute(sqlalchemy.text(potion_query))
        
        barrel_query = """
                    SELECT rgbd, 
                        SUM(ml) AS ml
                    FROM barrel_ledger
                    GROUP BY rgbd
                 """
        ml_table = connection.execute(sqlalchemy.text(barrel_query))
        ml = {row.rgbd: row.ml for row in ml_table}


        for potion in potions_table:
            if(
                potion.red_ml <= ml["[1, 0, 0, 0]"]
                and potion.blue_ml <= ml["[0, 1, 0, 0]"]
                and potion.green_ml <= ml["[0, 0, 1, 0]"]
                and potion.dark_ml <= ml["[0, 0, 0, 1]"]
            ):
                # TRY QUANTITY = AND DIV BY NEEDED MODULUS DIV
                bottle_plan.append({
                    "potion_type": [potion.red_ml,potion.blue_ml,potion.green_ml,potion.dark_ml],
                    "quantity": 1
                })

    print(f"Bottle plan:{bottle_plan}")
    return bottle_plan             

    # with db.engine.begin() as connection:

    #     bottle_plan = []
    #     potion_query = """
    #                     SELECT name, quantity,red_ml,blue_ml, green_ml, dark_ml
    #                     FROM potions
    #                    """
    #     potions_table = connection.execute(sqlalchemy.text(potion_query))
        
    #     ml_table = connection.execute(sqlalchemy.text("SELECT type, ml FROM barrels"))
    #     ml = {row.type: row.ml for row in ml_table}

    #     for potion in potions_table:
    #         if potion.red_ml <= ml["red"] and potion.blue_ml <= ml["blue"] and potion.green_ml <= ml["green"] and potion.dark_ml <= ml["dark"]:
    #             bottle_plan.append({
    #                 "potion_type": [potion.red_ml,potion.blue_ml,potion.green_ml,potion.dark_ml],
    #                 "quantity": 1
    #             })


    # print(f"Bottle plan:{bottle_plan}")
    # return bottle_plan             

if __name__ == "__main__":
    print(get_bottle_plan())
