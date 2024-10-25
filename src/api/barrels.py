from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ 
    Runs after the wholesale_plan is run and made, adds ml and subtracts gold from plan
    """

    with db.engine.begin() as connection:
        
        ml_table = connection.execute(sqlalchemy.text("SELECT type, ml FROM barrels"))
        ml = {row.type: row.ml for row in ml_table}
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()

        #run through barrel array and identify by potion type
        for barrel in barrels_delivered:
            ml_bought = barrel.ml_per_barrel
            cost = barrel.price

            if "RED" in barrel.sku:
                ml["red"] = ml["red"] + ml_bought
                gold = gold - cost
            elif "GREEN" in barrel.sku:
                ml["green"] = ml["green"] + ml_bought
                gold = gold - cost
            elif "BLUE" in barrel.sku:
                ml["blue"] = ml["blue"] + ml_bought
                gold = gold - cost
            elif "DARK" in barrel.sku:
                ml["dark"] = ml["dark"] + ml_bought
                gold = gold - cost

        #NOW UPDATE NEW VALUES
        query = f"""
                UPDATE barrels
                SET ml = CASE
                    WHEN id = 1 THEN {ml["red"]}
                    WHEN id = 2 THEN {ml["green"]}
                    WHEN id = 3 THEN {ml["blue"]}
                    WHEN id = 4 THEN {ml["dark"]}
                    END
                WHERE id > 0
                """
        connection.execute(sqlalchemy.text(query))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = '{gold}'"))
        
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    

    with db.engine.begin() as connection:
        green_stock = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id = 2")).scalar()
        red_stock = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id = 1")).scalar()
        blue_stock = connection.execute(sqlalchemy.text("SELECT quantity FROM potions WHERE id = 3")).scalar()

        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()
          
    barrel_plan = []
    
    for barrel in wholesale_catalog:
        if "RED" in barrel.sku:
            if red_stock < 4 and gold > barrel.price:
                gold -= barrel.price
                barrel_plan.append(
                {
                    "sku": barrel.sku,
                    "quantity": barrel.quantity
                })
        if "GREEN" in barrel.sku:
            if green_stock < 4 and gold > barrel.price:
                gold -= barrel.price
                barrel_plan.append(
                {
                    "sku": barrel.sku,
                    "quantity": barrel.quantity
                })
        if "BLUE" in barrel.sku:
            if blue_stock < 4 and gold > barrel.price:
                gold -= barrel.price
                barrel_plan.append(
                {
                    "sku": barrel.sku,
                    "quantity": barrel.quantity
                })
        # if "DARK" in barrel.sku:
        #     if   
                
    return barrel_plan

