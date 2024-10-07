from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

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

    # connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = '{potion_stock}', num_green_ml = '{quantity_ml}' WHERE id = 1"))

    return "OK"

