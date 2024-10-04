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
    """ """
    ml = barrels_delivered[0].ml_per_barrel
    cost = barrels_delivered[0].price
    with db.engine.begin() as connection:

        #grab current ml and gold first
        result_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        current_ml = int(result_ml.fetchone()[0]) + ml
        result_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        current_gold = int(result_gold.fetchone()[0]) - cost

        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = '{current_ml}', gold = '{current_gold}' WHERE id = 1"))
        

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        potion_stock = int(result.fetchone()[0])
    
    
    if potion_stock < 10:
        return [
        {   
            "sku": "SMALL_GREEN_BARREL",
            "quantity": 1,
        }
    ]
    
    else:
        return[]

