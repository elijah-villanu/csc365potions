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
    query = """
            TRUNCATE TABLE
            carts,
            cart_items,
            visitors,
            global_inventory
            """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(query))
        connection.execute(sqlalchemy.text("""
                                           INSERT INTO global_inventory (num_green_ml, num_red_ml, num_blue_ml, gold) 
                                           VALUES (0,0,0,100)
                                           """))
        connection.execute(sqlalchemy.text("UPDATE potions SET quantity = 0"))
        
        
    
    return "OK"

