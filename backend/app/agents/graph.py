import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.agents.state import ReceptionistState
from app.agents.nodes import detect_intent, receptionist_response
from app.agents.nodes import (
    detect_intent,
    extract_customer_details,
    receptionist_response
)


builder = StateGraph(ReceptionistState)

builder.add_node("detect_intent", detect_intent)
builder.add_node("extract_customer_details", extract_customer_details)
builder.add_node("receptionist_response", receptionist_response)

builder.add_edge(START, "detect_intent")
builder.add_edge("detect_intent", "extract_customer_details")
builder.add_edge("extract_customer_details", "receptionist_response")
builder.add_edge("receptionist_response", END)


conn = sqlite3.connect(
    "receptionist_checkpoints.sqlite",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn)

receptionist_graph = builder.compile(
    checkpointer=checkpointer
)
