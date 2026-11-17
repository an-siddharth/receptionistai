from app.agents.state import ReceptionistState
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)


class CustomerDetails(BaseModel):
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_location: str | None = None
    service_requested: str | None = None



def extract_customer_details(state: ReceptionistState):
    extractor = llm.with_structured_output(CustomerDetails)

    result = extractor.invoke([
        {
            "role": "system",
            "content": """
            Extract customer details from the conversation.
            Only extract explicitly provided information.
            The customer has provided their name and service request.
            Return null for missing information.
            """
        },
        *state["messages"]
    ])

    print("\nDEBUG — Extractor output:")
    print(result)

    extracted = {
        "customer_name": result.customer_name or state.get("customer_name"),
        "customer_phone": result.customer_phone or state.get("customer_phone"),
        "customer_location": result.customer_location or state.get("customer_location"),
        "service_requested": result.service_requested or state.get("service_requested")
    }

    print("\nDEBUG — State update:")
    print(extracted)

    return extracted



def detect_intent(state: ReceptionistState):
    latest_message = state["messages"][-1].content

    response = llm.invoke([
        {
            "role": "system",
            "content": """
You are an intent classifier for a plumbing and electrical
service company's AI receptionist.

Classify the customer's latest message into exactly ONE category:

book_appointment:
- Customer needs a plumber or electrician.
- Customer reports a problem that needs repair.
- Customer wants to schedule, book, or request a service.
- Examples: "I need a plumber", "My sink is leaking",
  "I want someone to fix my wiring."

ask_service:
- Customer asks what services the company offers.

ask_location:
- Customer asks where the business is located or its service area.

speak_to_human:
- Customer explicitly requests a human representative.

general_query:
- Greetings, casual conversation, or unrelated questions.

IMPORTANT:
- A request for repair or service is book_appointment,
  even if the customer hasn't explicitly mentioned booking.
- Return ONLY the category name.
"""
        },
        {
            "role": "user",
            "content": latest_message
        }
    ])

    content = response.content

    if isinstance(content, list):
        content = "".join(
            item["text"] if isinstance(item, dict) and "text" in item
            else str(item)
            for item in content
        )

    intent = content.strip().lower()

    valid_intents = [
        "book_appointment",
        "ask_service",
        "ask_location",
        "speak_to_human",
        "general_query"
    ]

    if intent not in valid_intents:
        intent = "general_query"

    print("\nDEBUG — Detected Intent:", intent)

    return {"intent": intent}




def receptionist_response(state: ReceptionistState):

    customer_details = {
        "name": state.get("customer_name"),
        "phone": state.get("customer_phone"),
        "location": state.get("customer_location"),
        "service": state.get("service_requested"),
        "appointment_date": state.get("appointment_date"),
        "appointment_time": state.get("appointment_time")
    }

    system_prompt = f"""
You are a friendly and professional AI receptionist
for a plumbing and electrical service company.

CUSTOMER INFORMATION COLLECTED:
{customer_details}

YOUR RESPONSIBILITIES:
1. Understand the customer's service requirements.
2. Collect their name, phone number and location.
3. Help them schedule appointments.
4. Answer basic questions about business services.
5. Ask for a preferred appointment date and time.

RULES:
- Keep responses short and conversational.
- Ask only ONE question at a time.
- Do not ask for information already collected.
- If the name is known, do not ask for it again.
- Collect missing details one by one.
- Never invent appointment availability.
- Never claim an appointment is booked unless it actually is.
- If the customer requests a human, acknowledge their request.
"""

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        *state["messages"]
    ])

    return {"messages": [response]}


