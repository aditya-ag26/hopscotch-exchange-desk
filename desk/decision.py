import json
from typing import Literal

from langchain_core.messages import ToolMessage

from desk.config import HIGH_VALUE, MAX_TRIPS, RETURN_WINDOW_DAYS, VENDOR_SPIKE
from desk.state import DeskState


def read_facts(messages: list) -> dict:
    facts = {}
    for m in messages:
        if isinstance(m, ToolMessage):
            facts[m.name] = json.loads(m.text)
    return facts


def policy_check(state: DeskState):
    facts = read_facts(state["messages"])
    claim = state["claim"]
    order = facts.get("get_order", {})
    pickup = facts.get("check_pickup", {})
    vendor = facts.get("get_vendor_return_rate", {})
    is_defect = claim["issue_type"] == "defect"

    if "days_since_delivery" not in order:
        exit, reason = "escalate", "order could not be found"
    elif order["days_since_delivery"] > RETURN_WINDOW_DAYS:
        exit, reason = "decline", f"outside the {RETURN_WINDOW_DAYS}-day return window"
    elif order["price"] > HIGH_VALUE:
        exit, reason = "escalate", f"order above INR {HIGH_VALUE}"
    elif pickup.get("serviceable") is not True:
        exit, reason = "escalate", "pickup not confirmed for this pincode"
    elif is_defect and "return_rate" not in vendor:
        exit, reason = "escalate", "defect claim but vendor return rate unknown"
    elif is_defect and vendor["return_rate"] >= VENDOR_SPIKE:
        exit, reason = "escalate", f"vendor {vendor['vendor_id']} return rate is {vendor['return_rate']}"
    else:
        exit, reason = "approve", f"{claim['issue_type']} within the window, pickup available"

    return {"exit": exit, "reason": reason}


def route_exit(state: DeskState) -> Literal["escalate", "respond"]:
    if state["exit"] == "escalate":
        return "escalate"
    return "respond"


ESCALATION_QUEUE = []


def escalate(state: DeskState):
    reason = state.get("reason") or f"tool loop went past {MAX_TRIPS} trips"
    ESCALATION_QUEUE.append({"message": state["message"], "reason": reason})
    return {"exit": "escalate", "reason": reason, "status": f"escalated: {reason}"}
