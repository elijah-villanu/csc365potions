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
 
        r_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar()
        g_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        b_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar()
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()

        #run through barrel array and identify by potion type
        for barrel in barrels_delivered:
            ml_bought = barrel.ml_per_barrel
            cost = barrel.price

            if "RED" in barrel.sku:
                r_ml = r_ml + ml_bought
                gold = gold - cost
            elif "GREEN" in barrel.sku:
                g_ml = g_ml + ml_bought
                gold = gold - cost
            elif "BLUE" in barrel.sku:
                b_ml = b_ml + ml_bought
                gold = gold - cost

        #NOW UPDATE NEW VALUES
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = '{r_ml}', gold = '{gold}' WHERE id = 1"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = '{g_ml}' WHERE id = 1"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml = '{b_ml}' WHERE id = 1"))

        
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    # print(wholesale_catalog)
    

    with db.engine.begin() as connection:
        green_stock = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        red_stock = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar()
        blue_stock = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar()

        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()
          
    barrel_plan = []
    
    for barrel in wholesale_catalog:
        if "RED" in barrel.sku:
            if red_stock < 4 and gold > barrel.price:
                barrel_plan.append(
                {
                    "sku": barrel.sku,
                    "quantity": barrel.quantity
                })
        if "GREEN" in barrel.sku:
            if green_stock < 4 and gold > barrel.price:
                barrel_plan.append(
                {
                    "sku": barrel.sku,
                    "quantity": barrel.quantity
                })
        if "BLUE" in barrel.sku:
            if blue_stock < 4 and gold > barrel.price:
                barrel_plan.append(
                {
                    "sku": barrel.sku,
                    "quantity": barrel.quantity
                })   
                
    return barrel_plan

