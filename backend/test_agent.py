
from app.agents.graph import receptionist_graph

config = {
    "configurable": {
        "thread_id": "customer-test-003"
    }
}

def send_message(message):
    global config

    result = receptionist_graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        },
        config=config
    )

    print("\nReceptionist:", result["messages"][-1].content)

    print("\n--- Customer Details ---")
    print("Name:", result.get("customer_name"))
    print("Phone:", result.get("customer_phone"))
    print("Location:", result.get("customer_location"))
    print("Service:", result.get("service_requested"))
    print("Intent:", result.get("intent"))


# Test conversation
send_message("Hi, I need a plumber for my leaking kitchen pipe.")

send_message("My name is Rahul Sharma.")
