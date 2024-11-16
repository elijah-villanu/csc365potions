from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db



router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   
"""
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """


@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc, #column for timestamp, defaults to desc
):
    
    all_customers_query =   """
                            SELECT DISTINCT ci.id, c.name AS customer_name, p.name AS item_sku, 
                                pl.price AS  line_item_total, pl.checkout_time AS timestamp
                            FROM potion_ledger AS pl
                            JOIN potions AS p ON p.potion_sku = pl.item_sku
                            JOIN cart_items AS ci ON ci.item_sku = pl.item_sku
                            JOIN carts AS c ON c.id = ci.cart_id
                            WHERE pl.is_checkout = true
                            GROUP BY ci.id, c.name, p.name, pl.price, pl.checkout_time
                       """
    cust_only_query =  """
                            SELECT DISTINCT ci.id, c.name AS customer_name, p.name AS item_sku, 
                                pl.price AS  line_item_total, pl.checkout_time AS timestamp
                            FROM potion_ledger AS pl
                            JOIN potions AS p ON p.potion_sku = pl.item_sku
                            JOIN cart_items AS ci ON ci.item_sku = pl.item_sku
                            JOIN carts AS c ON c.id = ci.cart_id
                            WHERE pl.is_checkout = true
                                AND c.name ILIKE :customer_name
                            GROUP BY ci.id, c.name, p.name, pl.price, pl.checkout_time
                        """
    pot_only_query = """
                            SELECT DISTINCT ci.id, c.name AS customer_name, p.name AS item_sku, 
                                pl.price AS  line_item_total, pl.checkout_time AS timestamp
                            FROM potion_ledger AS pl
                            JOIN potions AS p ON p.potion_sku = pl.item_sku
                            JOIN cart_items AS ci ON ci.item_sku = pl.item_sku
                            JOIN carts AS c ON c.id = ci.cart_id
                            WHERE pl.is_checkout = true
                                AND p.name ILIKE :potion_sku
                            GROUP BY ci.id, c.name, p.name, pl.price, pl.checkout_time
                     """
    both_query = """
                            SELECT DISTINCT ci.id, c.name AS customer_name, p.name AS item_sku, 
                                pl.price AS  line_item_total, pl.checkout_time AS timestamp
                            FROM potion_ledger AS pl
                            JOIN potions AS p ON p.potion_sku = pl.item_sku
                            JOIN cart_items AS ci ON ci.item_sku = pl.item_sku
                            JOIN carts AS c ON c.id = ci.cart_id
                            WHERE pl.is_checkout = true
                                AND c.name ILIKE :customer_name
                                AND p.name ILIKE :potion_sku
                            GROUP BY ci.id, c.name, p.name, pl.price, pl.checkout_time
                     """
    customer_search = []
    all_customers = []
    sorting_clause = f"\nORDER BY {sort_col.value} {sort_order.value};"

    with db.engine.begin() as conn:
        # Full search
        if customer_name == "" and potion_sku == "":
            all_customers_query += sorting_clause
            all_customers = conn.execute(sqlalchemy.text(all_customers_query))
        elif potion_sku =="":
            customer_name += "%"
            cust_only_query += sorting_clause
            all_customers = conn.execute(sqlalchemy.text(cust_only_query),{"customer_name":customer_name})
        elif customer_name =="":
            potion_sku += "%"
            pot_only_query += sorting_clause
            all_customers = conn.execute(sqlalchemy.text(pot_only_query),{"potion_sku":potion_sku})
        else:
            potion_sku += "%"
            customer_name += "%"
            both_query += sorting_clause
            all_customers = conn.execute(sqlalchemy.text(both_query),{"customer_name":customer_name,
                                                                      "potion_sku":potion_sku})

    
    for customer in all_customers:
        customer_search.append({
            "line_item_id": customer.id,
            "item_sku": customer.item_sku,
            "customer_name": customer.customer_name,
            "line_item_total": customer.line_item_total,
            "timestamp": customer.timestamp
        })

    
    return {
        "previous": "",
        "next": "",
        "results": customer_search
        
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """

    # with db.engine.begin() as conn:
    #     for customer 
    #     conn.execute(sqlalchemy.text("""
    #                                 INSERT INTO visitors 
    #                                 (id, name, class, level)
    #                                 VALUES (:id, :name, :class, :level)
    #                                 """), {"id":new_id
    #                                        "name":})
    # print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    # Insert new row each cart id and append by one for the id (sequential id)
    with db.engine.begin() as connection:
        new_id = connection.execute(sqlalchemy.text("SELECT MAX(id) FROM carts")).scalar() + 1
        new_cart_query = """
                            INSERT INTO carts
                                (id, name, class)
                            VALUES
                                (:new_id, :name, :class)
                         """
        connection.execute(sqlalchemy.text(new_cart_query), {"new_id": new_id,
                                                             "name": new_cart.customer_name,
                                                             "class": new_cart.character_class})
    return {"cart_id": new_id} 


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    quantity = cart_item.quantity

    with db.engine.begin() as connection:

        price_query = """
                        SELECT price
                            FROM potions
                        WHERE potion_sku = :item_sku
                      """
        cart_item_query =   """
                                INSERT INTO cart_items
                                    (cart_id, item_sku, quantity, total)
                                VALUES
                                    (:cart_id, :item_sku, :quantity, :total) 
                            """
        price = connection.execute(sqlalchemy.text(price_query),{"item_sku": item_sku}).scalar()
        total = price * quantity
        connection.execute(sqlalchemy.text(cart_item_query), {"cart_id":cart_id,
                                                              "item_sku":item_sku, 
                                                              "quantity":quantity,
                                                              "total":total})
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    # Ledgerize purchase: rgbd, profit, (-)quantity, cart_id !!! Do in checkout    
    with db.engine.begin() as connection:
        # using cart_id grab their row and look through each column to decide what to buy

        cart_items_query = """
                            SELECT ci.item_sku, ci.quantity, ci.total,
                                p.rgbd, ci.cart_id
                            FROM cart_items AS ci
                            LEFT JOIN potions AS p ON p.potion_sku = ci.item_sku
                            WHERE cart_id = :cart_id
                           """
        cart_items_table = connection.execute(sqlalchemy.text(cart_items_query),{"cart_id": cart_id})

        add_ledger = []

        total_quant = 0
        total_cost = 0
        for item in cart_items_table:
            sold_quantity = -item.quantity
            total_quant += item.quantity
            total_cost += item.total
            add_ledger.append({
                "rgbd": item.rgbd,
                "price": item.total,
                "quantity": sold_quantity,
                "cart_id": item.cart_id,
                "item_sku": item.item_sku,
                "checkout": True
            })
            
        # Update potion ledger
        ledger_query =  """
                            INSERT INTO potion_ledger
                                (rgbd, price, quantity, cart_id, item_sku, is_checkout)
                            VALUES (:rgbd, :price, :quantity, :cart_id, :item_sku, :checkout)
                        """
        connection.execute(sqlalchemy.text(ledger_query), add_ledger)

        
    return {"total_potions_bought": total_quant, "total_gold_paid": total_cost}
