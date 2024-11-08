from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    truncate_query = """
            TRUNCATE TABLE
            cart_items,
            visitors,
            barrel_ledger
                """
    cart_query ="""
                DELETE FROM carts
                WHERE id != 0
                """
    
    # at id = 0 is all null except for gold = 100 (acts as starting value)
    gold_query =  """
                DELETE FROM potion_ledger
                WHERE id != 0 
                """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(truncate_query))
        connection.execute(sqlalchemy.text(cart_query))
        connection.execute(sqlalchemy.text(gold_query))
        
        
    
    return "OK"

