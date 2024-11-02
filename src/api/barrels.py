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
    SHOULD HAVE SQL UPDATE
    """

    with db.engine.begin() as connection:
        
        ml_table = connection.execute(sqlalchemy.text("SELECT rgbd, ml FROM barrels"))
        ml = {row.rgbd: row.ml for row in ml_table}
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()

        query = f"""
                UPDATE barrels
                SET ml = CASE
                """
        query_updated = False

        #run through barrel plan and identify by potion type
        for purchased in barrels_delivered:
            ml_bought = purchased.ml_per_barrel
            if ml_bought > 0:
                cost = purchased.price
                type = str(purchased.potion_type)
                ml[type] += ml_bought
                gold -= cost
            
                barrel_query = f"WHEN rgbd = '{type}' THEN {ml[type]} \n"
                query += barrel_query
                query_updated = True


        #SQL UPDATE NEW VALUES (Only Runs if barrels were actually bought)
        query += "END"    
        if query_updated:    
            connection.execute(sqlalchemy.text(query))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = '{gold}'"))
        
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    
    barrel_plan = []

    with db.engine.begin() as conn:
        barrel_table = conn.execute(sqlalchemy.text("SELECT * FROM barrels"))
        gold = conn.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()
        barrels = {row.rgbd:row.ml for row in barrel_table}

        for purchase in wholesale_catalog:
            barrel_type = str(purchase.potion_type)
            if barrels[barrel_type] <= 100 and gold > purchase.price:
                barrel_plan.append({
                    "sku": purchase.sku,
                    "quantity": 1
                })
        print(barrel_plan)
        return barrel_plan            
    

