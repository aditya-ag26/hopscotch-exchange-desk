from langchain_core.messages import AIMessage

from desk.gate import gate
from desk.graph import build_graph
from desk.tools import TOOLS
from test_messages import MESSAGES


def show_run(final_state: dict):
    print("Claim:", final_state.get("claim"))
    print("Tone:", final_state.get("tone"))

    trip = 0
    for m in final_state.get("messages", []):
        if isinstance(m, AIMessage) and m.tool_calls:
            trip = trip + 1
            print(f"Trip {trip}:", [f"{c['name']}({c['args']})" for c in m.tool_calls])

    if final_state.get("exit"):
        print(f"Exit: {final_state['exit']} | {final_state['reason']}")
        print(f"Status: {final_state['status']}")
    if final_state.get("reply"):
        print(f"Reply: {final_state['reply']}")


if __name__ == "__main__":
    app = build_graph(TOOLS)

    for name, text in MESSAGES.items():
        print(f"\n== {name}")

        status = gate(text)
        if status != "accepted":
            print(status)
            continue

        final_state = app.invoke({"message": text})
        show_run(final_state)
