import requests
from langchain_core.tools import tool

from desk import config
from desk.data import ORDERS, VENDOR_SALES


@tool
def get_order(order_id: str) -> dict:
    """Look up a Hopscotch order by its id (for example HS2291).
    Returns the item, size, vendor_id, price in INR and days since delivery."""
    order_id = order_id.upper()
    if order_id not in ORDERS:
        return {"order_id": order_id, "error": "order not found"}

    result = ORDERS[order_id].copy()
    result["order_id"] = order_id
    return result


@tool
def check_pickup(pincode: str) -> dict:
    """Check whether a reverse pickup can be booked at a 6-digit Indian pincode.
    Use it only when the customer wants the item picked up and has given a pincode."""
    try:
        r = requests.get(config.PINCODE_API + pincode, timeout=5, headers={"User-Agent": "hopscotch-exchange-desk/1.0"})
        data = r.json()[0]
    except Exception as e:
        return {"pincode": pincode, "error": f"pickup check failed: {type(e).__name__}"}

    if data["Status"] != "Success":
        return {"pincode": pincode, "serviceable": False}

    serviceable = False
    for office in data["PostOffice"]:
        if office["DeliveryStatus"] == "Delivery":
            serviceable = True
    return {"pincode": pincode, "serviceable": serviceable}


@tool
def get_vendor_return_rate(vendor_id: str) -> dict:
    """Get a vendor's return rate in percent. The vendor_id of an order comes from get_order.
    Use it only for defect claims (broken, torn, faded, stitching)."""
    if vendor_id not in VENDOR_SALES:
        return {"vendor_id": vendor_id, "error": "vendor not found"}

    sales = VENDOR_SALES[vendor_id]
    rate = round(sales["units_returned"] / sales["units_sold"] * 100, 2)
    return {"vendor_id": vendor_id, "return_rate": rate}


TOOLS = [get_order, check_pickup, get_vendor_return_rate]


if __name__ == "__main__":
    print(get_order.invoke({"order_id": "HS2291"}))
    print(check_pickup.invoke({"pincode": "122002"}))
    print(get_vendor_return_rate.invoke({"vendor_id": "V5"}))
