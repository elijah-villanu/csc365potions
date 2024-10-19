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
    #SQL UPDATE to set gold and potions
    columns = ["red","green","blue"]
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = '100' WHERE id = 1"))    
        for color in columns:
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_{color}_potions = '0', num_{color}_ml = '0' WHERE id = 1"))
        connection.execute(sqlalchemy.text("DELETE FROM carts WHERE id != 0"))
    

    return "OK"

