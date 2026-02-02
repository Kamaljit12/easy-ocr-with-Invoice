from typing import Union, Dict, Any
from schemas import InvoiceState

def apply_human_input(
    state: Union[InvoiceState, Dict[str, Any]],
    human_data: Dict[str, Any]) -> InvoiceState:

    if isinstance(state, InvoiceState):
        state = dict(state)

    missing_fields = state.get("missing_fields", [])

    for field in missing_fields:
        print(f"Please provide the value for {field}")

    print("-" * 20)

    for k, v in human_data.items():
        if k in missing_fields and v is not None:
            state[k] = v
            missing_fields.remove(k)

    state["missing_fields"] = missing_fields
    state["status"] = "processing"

    return InvoiceState(**state)

