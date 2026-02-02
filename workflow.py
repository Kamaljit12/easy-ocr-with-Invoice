# workflow.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from schemas import InvoiceState
from utils import (
    validate_invoice,
    confidence_agent,
    human_review,
    route_after_validation
)
from services import extract_invoice_fields


memory = InMemorySaver()

def get_workflow():
    graph = StateGraph(InvoiceState)

    graph.add_node("extract", extract_invoice_fields)
    graph.add_node("confidence", confidence_agent)
    graph.add_node("validate", validate_invoice)
    graph.add_node("human_review", human_review)

    graph.add_edge(START, "extract")
    graph.add_edge("extract", "confidence")
    graph.add_edge("confidence", "validate")

    graph.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "human_review": "human_review",
            "end": END,
        },
    )

    # HITL pause point
    graph.add_edge("human_review", END)

    return graph.compile(checkpointer=memory)
