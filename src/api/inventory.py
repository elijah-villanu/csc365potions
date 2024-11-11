from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import math

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """
    Return a summary of your current number of
    potions, ml, and gold. 
    """
    with db.engine.begin() as connection:
        ml_query = """
                    SELECT SUM(red_ml) AS red_ml, SUM(blue_ml) AS blue_ml, 
                        SUM(green_ml) AS green_ml, SUM(dark_ml) AS dark_ml,
                        SUM(cost) AS cost
                    FROM barrel_ledger
                   """
        ml_values = connection.execute(sqlalchemy.text(ml_query))
        ml_total = 0
        cost = 0
        for row in ml_values:
            ml_total += row.red_ml + row.blue_ml + row.green_ml + row.dark_ml
            cost += row.cost

        potion_query = """
                        SELECT SUM(quantity) AS quantity, SUM(price) AS profit
                        FROM potion_ledger
                       """
        stock_values = connection.execute(sqlalchemy.text(potion_query))
        stock_total = 0
        profit = 0
        for row in stock_values:
            stock_total += row.quantity
            profit += row.profit
        
        # Cost is already negative on tables
        gold = profit + cost
    print(f"number_of_potions: {stock_total} ml_in_barrels: {ml_total}, gold: {gold}")
        
    return {"number_of_potions": stock_total, "ml_in_barrels": ml_total, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
