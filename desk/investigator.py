from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage

from desk.config import MAX_TRIPS, llm
from desk.state import DeskState

INVESTIGATOR_PROMPT = """You gather facts for Hopscotch's exchange desk. You only look things up; you never decide the outcome.
Use the tools like this:
- get_order: always, if the claim has an order id.
- check_pickup: only if the customer wants an exchange or refund and gave a pincode.
- get_vendor_return_rate: only for a defect claim, with the vendor_id that get_order returned.
Ask for tools that do not depend on each other in the same turn.
When you have the facts this claim needs, stop calling tools and reply with one word: DONE."""


def make_investigator(tools: list):
    llm_with_tools = llm.bind_tools(tools)

    def investigator(state: DeskState):
        request = HumanMessage(
            f"Claim: {state['claim']}\n"
            f"Tone: {state['tone']}\n"
            f"Customer message: {state['message']}"
        )
        conversation = [SystemMessage(INVESTIGATOR_PROMPT), request] + state.get("messages", [])
        response = llm_with_tools.invoke(conversation)

        trips = state.get("trips", 0)
        if response.tool_calls:
            trips = trips + 1
        return {"messages": [response], "trips": trips}

    return investigator


def after_investigator(state: DeskState) -> Literal["tools", "policy_check", "escalate"]:
    if not state["messages"][-1].tool_calls:
        return "policy_check"
    if state["trips"] > MAX_TRIPS:
        return "escalate"
    return "tools"
