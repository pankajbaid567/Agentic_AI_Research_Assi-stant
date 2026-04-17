import sys
import os

# Ensure the parent directory is in the path to import agent_state
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langgraph.graph import StateGraph, START, END
from agent_state import AgentState, create_initial_state

# Import node functions directly since parent directory is in sys.path
from search_node import search_node
from summarize_node import summarize_node
from validate_node import validate_node
from report_node import report_node

# 5. Build simple error_handler_node inline
def error_handler_node(state: AgentState) -> AgentState:
    """Builds a minimal error report based on logs."""
    state["final_report"] = {
        "status": "failed",
        "error_details": "Graph execution failed. See logs for detailed errors.",
        "logs": state.get("error_log", [])
    }
    state["current_step"] = "done_with_error"
    return state

# 1. Build the conditional edge function
def route_after_validation(state: AgentState) -> str:
    """Routes to retry search, handle errors, or proceed to report."""
    if state.get("current_step") == "error":
        return "error_handler_node"
        
    flags = state.get("validation_flags", [])
    # validation failed if no flags are True
    validation_failed = (not flags) or (not any(flags))
    
    if validation_failed:
        iteration = state.get("iteration_count", 0)
        if iteration < 3:
            return "search_node"
        else:
            return "error_handler_node"
            
    return "report_node"

# 2. Build the StateGraph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("search_node", search_node)
workflow.add_node("summarize_node", summarize_node)
workflow.add_node("validate_node", validate_node)
workflow.add_node("report_node", report_node)
workflow.add_node("error_handler_node", error_handler_node)

# Add standard edges
workflow.add_edge(START, "search_node")
workflow.add_edge("search_node", "summarize_node")
workflow.add_edge("summarize_node", "validate_node")

# Add conditional edge from validate_node
workflow.add_conditional_edges(
    "validate_node",
    route_after_validation,
    {
        "search_node": "search_node",
        "error_handler_node": "error_handler_node",
        "report_node": "report_node"
    }
)

# Add ending edges
workflow.add_edge("report_node", END)
workflow.add_edge("error_handler_node", END)

# 3. Compile the graph
research_graph = workflow.compile()

# 4. Expose a clean runner
def run_research(query: str) -> dict:
    state = create_initial_state(query)
    result = research_graph.invoke(state)
    return result
