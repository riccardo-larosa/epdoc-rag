from typing import TypedDict, Annotated, Union
from operator import add
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

# Define our state
class OrderQueryState(TypedDict):
    messages: Annotated[list[Union[HumanMessage, AIMessage]], add]
    query: str
    order_data: dict
    confidence: float

# Mock functions for our nodes
def process_query(state: OrderQueryState) -> OrderQueryState:
    # In a real system, this would analyze the query
    state['query'] = state['messages'][-1].content
    return state

def query_database(state: OrderQueryState) -> OrderQueryState:
    # Mock database query
    state['order_data'] = {"order_id": "12345", "status": "shipped"}
    return state

def evaluate_confidence(state: OrderQueryState) -> OrderQueryState:
    # Mock confidence evaluation
    state['confidence'] = 0.8
    return state

def generate_response(state: OrderQueryState) -> OrderQueryState:
    response = f"Based on the order data: {state['order_data']}, your order status is {state['order_data']['status']}."
    state['messages'].append(AIMessage(content=response))
    return state

def generate_uncertainty_response(state: OrderQueryState) -> OrderQueryState:
    response = "I'm sorry, but I don't have enough information to confidently answer your query."
    state['messages'].append(AIMessage(content=response))
    return state

# Create the graph
workflow = StateGraph(OrderQueryState)

# Add nodes
workflow.add_node("process_query", process_query)
workflow.add_node("query_database", query_database)
workflow.add_node("evaluate_confidence", evaluate_confidence)
workflow.add_node("generate_response", generate_response)
workflow.add_node("generate_uncertainty_response", generate_uncertainty_response)

# Add edges
workflow.set_entry_point("process_query")
workflow.add_edge("process_query", "query_database")
workflow.add_edge("query_database", "evaluate_confidence")

# Conditional edge based on confidence
def route_on_confidence(state: OrderQueryState):
    return "generate_response" if state['confidence'] >= 0.7 else "generate_uncertainty_response"

workflow.add_conditional_edges(
    "evaluate_confidence",
    route_on_confidence,
    {
        "generate_response": "generate_response",
        "generate_uncertainty_response": "generate_uncertainty_response"
    }
)

# Both response nodes lead to END
workflow.add_edge("generate_response", END)
workflow.add_edge("generate_uncertainty_response", END)

# Compile the graph
app = workflow.compile()

# Example usage
initial_state = {
    "messages": [HumanMessage(content="What's the status of my order?")],
    "query": "",
    "order_data": {},
    "confidence": 0.0
}

result = app.invoke(initial_state)
print(result['messages'][-1].content)