from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from desk.config import llm
from desk.state import DeskState

REPLY_PROMPT = """Write a reply to this Hopscotch customer in under 80 words.
Customer message: {message}
Decision: {exit}, because {reason}
Action taken: {action}
The customer sounds {tone}: if upset or angry, open with a short apology.
If approved, say a pickup is booked and the {wants} follows once the item is collected.
If declined, explain the reason kindly. Promise nothing else.
Mention order {order_id}. Sign as Hopscotch Support. Do not use placeholders."""


def respond(state: DeskState):
    order_id = state["claim"]["order_id"]

    if state["exit"] == "approve":
        action = f"pickup booked: PU-{order_id}"
    else:
        action = f"ticket closed: {order_id}"

    tem = PromptTemplate(
        template=REPLY_PROMPT,
        input_variables=["message", "exit", "reason", "action", "tone", "wants", "order_id"],
    )
    chain = tem | llm | StrOutputParser()
    reply = chain.invoke({
        "message": state["message"],
        "exit": state["exit"],
        "reason": state["reason"],
        "action": action,
        "tone": state["tone"],
        "wants": state["claim"]["wants"],
        "order_id": order_id,
    })
    return {"action": action, "reply": reply, "status": "reply sent"}
