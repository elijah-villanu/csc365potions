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

    # LEDGERIZE THIS 
    with db.engine.begin() as connection:
        ledger_id = connection.execute(sqlalchemy.text("SELECT max(id) FROM barrel_ledger")).scalar()
      
        barrel_add = []

        for purchased in barrels_delivered:
            ml_bought = purchased.ml_per_barrel
            price = purchased.price
            rgbd = str(purchased.potion_type)
            barrel_sku = purchased.sku
            cost = -purchased.price
            if ml_bought > 0:
                ledger_id += 1
                barrel_add.append({
                    "id" : ledger_id,
                    "rgbd" : rgbd,
                    "cost" : cost,
                    "ml" : ml_bought,
                    "sku" : barrel_sku
                })

        query = """
                INSERT INTO barrel_ledger
                    (id, rgbd, cost, ml, sku)
                VALUES
                    (:id, :rgbd, :cost, :ml, :sku)
                """
        # Runs as bulk update
        connection.execute(sqlalchemy.text(query), barrel_add)
        
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    #ONLY LOOK AT ML, NOT POT QUANT
    print(wholesale_catalog)
    
    barrel_plan = []

    #LEDGERIZE THIS
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
                                SUM(profit) AS gold
                            FROM potion_ledger 
                        """
        gold = conn.execute(sqlalchemy.text(gold_query)).scalar()

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

        for purchase in wholesale_catalog:
            type = str(purchase.potion_type)
            if barrels[type] <= 100 and gold > purchase.price:
                gold -=purchase.price
                barrel_plan.append({
                    "sku": purchase.sku,
                    "quantity": 1
                })
        print(barrel_plan)
        return barrel_plan        
    

