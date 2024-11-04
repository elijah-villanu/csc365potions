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

    # Potential query, normal join barrels table and potions and clear quant?
    
    truncate_query = """
            TRUNCATE TABLE
            carts,
            cart_items,
            visitors,
            global_inventory
            """
    ml_query = """
            UPDATE barrels SET ml = 0
            """
    potion_query = """
                UPDATE potions SET quantity = 0
                """
    gold_query ="""
            INSERT INTO global_inventory (gold,id) VALUES (100,1)
            """
    cart_query ="""
                INSERT INTO carts (id) VALUES (0)
                """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(truncate_query))
        connection.execute(sqlalchemy.text(ml_query))
        connection.execute(sqlalchemy.text(potion_query))
        connection.execute(sqlalchemy.text(gold_query))
        connection.execute(sqlalchemy.text(cart_query))
        
        
    
    return "OK"

