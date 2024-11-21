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
      
        barrel_add = []
        types = {
            '[1, 0, 0, 0]':"red_ml",
            '[0, 1, 0, 0]' : "green_ml",
            '[0, 0, 1, 0]' : "blue_ml",
            '[0, 0, 0, 1]' : "dark_ml"
        }
        
        for purchased in barrels_delivered:
            ml_in_barrel = {
            'red_ml': 0,
            'green_ml': 0,
            'blue_ml': 0,
            'dark_ml': 0
            }

            rgbd = str(purchased.potion_type)
            barrel_type = types[rgbd]

            #adds either red, green, blue or dark
            ml_in_barrel[barrel_type] += purchased.ml_per_barrel
            barrel_sku = purchased.sku
            cost = -purchased.price
                
            barrel_add.append({
                "rgbd" : rgbd,
                "cost" : cost,
                "sku" : barrel_sku,
                "red_ml": ml_in_barrel["red_ml"],
                "green_ml": ml_in_barrel["green_ml"],
                "blue_ml": ml_in_barrel["blue_ml"],
                "dark_ml": ml_in_barrel["dark_ml"]
                })

        query = """
                INSERT INTO barrel_ledger
                    (rgbd, cost, sku, red_ml, green_ml, blue_ml, dark_ml)
                VALUES
                    (:rgbd, :cost, :sku, :red_ml, :green_ml, :blue_ml, :dark_ml)
                """
        # Runs as bulk update
        connection.execute(sqlalchemy.text(query), barrel_add)
        
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    
    barrel_plan = []

    
    # DO CHECK CONSTRAINTSSS
    # Implement visitors!!
    with db.engine.begin() as conn:
        barrel_query =  """
                        SELECT 
                            SUM(red_ml) AS red,
                            SUM(green_ml) AS green,
                            SUM(blue_ml) AS blue,
                            SUM(dark_ml) AS dark,
                            rgbd
                        FROM barrel_ledger
                        GROUP BY rgbd
                        """
        barrel_table = conn.execute(sqlalchemy.text(barrel_query))

        gold_query =    """
                            SELECT
                                SUM(price) AS gold
                            FROM potion_ledger 
                        """
        profit = conn.execute(sqlalchemy.text(gold_query)).scalar()
        cost = conn.execute(sqlalchemy.text("SELECT SUM(cost) FROM barrel_ledger")).scalar()
        gold = profit + cost

        barrels = {}
        for row in barrel_table:
            rgbd = str(row.rgbd)
            ml = 0
            if row.red != 0:
                ml = row.red
            if row.green != 0:
                ml = row.green
            if row.blue != 0:
                ml = row.blue
            if row.dark != 0:
                ml = row.dark
            barrels[rgbd] = int(ml)

        print(barrels)

        check_constraint = 10000
        for purchase in wholesale_catalog:
            type = str(purchase.potion_type)
            if barrels[type] <= 100 and barrels[type]:
                gold -=purchase.price
                barrels[type] += purchase.ml_per_barrel
                barrel_plan.append({
                    "sku": purchase.sku,
                    "quantity": 1
                })
        print(barrel_plan)
        return barrel_plan        
    

