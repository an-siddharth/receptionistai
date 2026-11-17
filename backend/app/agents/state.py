from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class ReceptionistState(TypedDict):
    messages: Annotated[list, add_messages]

    customer_name: Optional[str]
    customer_phone: Optional[str]
    customer_location: Optional[str]

    service_requested: Optional[str]
    appointment_date: Optional[str]
    appointment_time: Optional[str]

    intent: Optional[str]
    booking_status: Optional[str]