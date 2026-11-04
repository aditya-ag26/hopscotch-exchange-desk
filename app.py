import streamlit as st
from langchain_core.messages import AIMessage

from desk.gate import gate
from desk.graph import build_graph
from desk.tools import TOOLS
from test_messages import MESSAGES

st.set_page_config(page_title="Hopscotch Exchange Desk", layout="wide")
st.title("Hopscotch Exchange Desk")

MODEL = "#fff3b0"
TOOLNODE = "#ffd8a8"
PLAIN = "#ffffff"
HIT = "#1e88e5"

NODES = {
    "message": dict(label="Customer message", shape="ellipse", fill=PLAIN),
    "gate": dict(label="gate", shape="box", fill=PLAIN),
    "reject": dict(label="rejected", shape="plaintext", fill=PLAIN),
    "extract_claim": dict(label="extract_claim", shape="box", fill=MODEL),
    "read_tone": dict(label="read_tone", shape="box", fill=MODEL),
    "investigator": dict(label="investigator", shape="box", fill=MODEL),
    "tools": dict(label="tools", shape="box", fill=TOOLNODE),
    "policy_check": dict(label="policy_check", shape="diamond", fill=PLAIN),
    "Escalate": dict(label="Escalate", shape="box", fill=PLAIN),
    "Decline": dict(label="Decline", shape="box", fill=PLAIN),
    "Approve": dict(label="Approve", shape="box", fill=PLAIN),
    "respond": dict(label="respond", shape="box", fill=MODEL),
    "END": dict(label="END", shape="ellipse", fill=PLAIN),
}

# (from, to, label, dashed)
EDGES = [
    ("message", "gate", "", False),
    ("gate", "reject", "too short / link / off-topic", False),
    ("gate", "extract_claim", "", False),
    ("gate", "read_tone", "", False),
    ("extract_claim", "investigator", "claim", False),
    ("read_tone", "investigator", "tone", False),
    ("investigator", "tools", "tool_calls", False),
    ("tools", "investigator", "results", False),
    ("investigator", "policy_check", "no tool_calls", False),
    ("investigator", "Escalate", "4 trips hit", True),
    ("policy_check", "Escalate", "", True),
    ("policy_check", "Decline", "", True),
    ("policy_check", "Approve", "", True),
    ("Decline", "respond", "", False),
    ("Approve", "respond", "", False),
    ("respond", "END", "", False),
]


@st.cache_resource
def get_app():
    return build_graph(TOOLS)


def draw(route: dict, active: str | None = None) -> str:
    lit = {n for edge in route for n in edge}
    out = [
        "digraph G {",
        'rankdir=TB; bgcolor="transparent"; nodesep=0.5; ranksep=0.45;',
        'node [style="rounded,filled", fontname="Helvetica", fontsize=12, color="#555555"];',
        'edge [fontname="Helvetica", fontsize=9, color="#999999", fontcolor="#777777"];',
        "{rank=same; gate; reject;}",
        "{rank=same; extract_claim; read_tone;}",
        "{rank=same; investigator; tools;}",
        "{rank=same; Escalate; Decline; Approve;}",
    ]
    for name, n in NODES.items():
        style = '"filled"' if n["shape"] in ("diamond", "ellipse", "plaintext") else '"rounded,filled"'
        attrs = f'label="{n["label"]}", shape={n["shape"]}, fillcolor="{n["fill"]}", style={style}'
        if name == active:
            attrs += f', color="{HIT}", penwidth=3, fillcolor="#e3f2fd"'
        elif name in lit:
            attrs += f', color="{HIT}", penwidth=2.5'
        else:
            attrs += ', fontcolor="#888888"'
        if name == "reject" and name in lit:
            attrs += ', fontcolor="#d32f2f"'
        out.append(f"{name} [{attrs}];")
    for a, b, label, dashed in EDGES:
        count = route.get((a, b), 0)
        text = label + (f" x{count}" if count > 1 else "")
        attrs = [f'label=" {text}"'] if text else []
        if dashed:
            attrs.append("style=dashed")
        if (a, b) in [("tools", "investigator")]:
            attrs.append("constraint=false")
        if count:
            attrs += [f'color="{HIT}"', f'fontcolor="{HIT}"', "penwidth=2.5"]
        out.append(f"{a} -> {b} [{', '.join(attrs)}];")
    out.append("}")
    return "\n".join(out)


def step(route: dict, last: list, node: str, update: dict):
    def hit(a, b):
        route[(a, b)] = route.get((a, b), 0) + 1

    if node in ("extract_claim", "read_tone"):
        hit("gate", node)
    elif node == "investigator":
        if last and last[-1] == "tools":
            hit("tools", "investigator")
        else:
            hit("extract_claim", "investigator")
            hit("read_tone", "investigator")
    elif node == "tools":
        hit("investigator", "tools")
    elif node == "policy_check":
        hit("investigator", "policy_check")
        exit_ = (update or {}).get("exit")
        if exit_:
            hit("policy_check", exit_.capitalize())
    elif node == "escalate":
        if "policy_check" not in last:
            hit("investigator", "Escalate")
    elif node == "respond":
        exit_ = "Approve" if ("policy_check", "Approve") in route else "Decline"
        hit(exit_, "respond")
        hit("respond", "END")
    last.append(node)


examples = {"(write your own)": "", **MESSAGES}
pick = st.selectbox("Example", list(examples))
text = st.text_area("Customer message", value=examples[pick], height=100)
run = st.button("Run", type="primary")

left, right = st.columns([1, 1])
with left:
    st.subheader("Route")
    graph_box = st.empty()
    graph_box.graphviz_chart(draw({}))

if run and text.strip():
    route, last, state = {("message", "gate"): 1}, [], {}
    status = gate(text)
    if status != "accepted":
        route[("gate", "reject")] = 1
        graph_box.graphviz_chart(draw(route, "reject"))
        right.error(f"Gate {status}")
        st.stop()

    graph_box.graphviz_chart(draw(route, "gate"))
    with right, st.status("Running...", expanded=True) as box:
        for mode, chunk in get_app().stream({"message": text}, stream_mode=["updates", "values"]):
            if mode == "values":
                state = chunk
                continue
            for node, update in chunk.items():
                step(route, last, node, update)
                st.write(f"✓ {node}")
                graph_box.graphviz_chart(draw(route, node))
        box.update(label="Done", state="complete", expanded=False)

    exit_ = state.get("exit")
    graph_box.graphviz_chart(draw(route, "END" if state.get("reply") else "Escalate"))

    with right:
        show = {"approve": st.success, "decline": st.warning}.get(exit_, st.info)
        show(f"**{(exit_ or '').upper()}**: {state.get('reason')}")

        if state.get("reply"):
            st.subheader("Reply")
            st.write(state["reply"])

        with st.expander("Details"):
            st.write("**Claim:**", state.get("claim"))
            st.write("**Tone:**", state.get("tone"))
            trips = [m.tool_calls for m in state.get("messages", []) if isinstance(m, AIMessage) and m.tool_calls]
            for i, calls in enumerate(trips, 1):
                st.write(f"**Trip {i}:**", [f"{c['name']}({c['args']})" for c in calls])
            st.write("**Status:**", state.get("status"))
