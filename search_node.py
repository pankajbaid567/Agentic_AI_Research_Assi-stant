import os
from dotenv import load_dotenv

# Import the TypedDict from the previous step
try:
    from agent_state import AgentState
except ImportError:
    from typing import Any
    AgentState = Any  # type: ignore

def search_node(state: AgentState) -> AgentState:
    load_dotenv()
    
    query = state.get("refined_query") if state.get("refined_query") else state.get("query", "")
    results = []
    
    # Ensure error_log exists
    if "error_log" not in state:
        state["error_log"] = []
    
    # PRIMARY: Tavily API
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    if tavily_api_key:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_api_key)
            # Execute search with potential timeout/rate-limit exceptions caught below
            response = client.search(
                query,
                max_results=5,
                search_depth="advanced"
            )
            for item in response.get("results", []):
                results.append({
                    "url": item.get("url", ""),
                    "title": item.get("title", ""),
                    "content": item.get("content", "")
                })
        except Exception as e:
            state["error_log"].append(f"Tavily search error (Rate Limit/Timeout/Other): {str(e)}")
    else:
        state["error_log"].append("TAVILY_API_KEY missing in environment.")

    # FALLBACK: DuckDuckGo
    if not results:
        try:
            from duckduckgo_search import DDGS
            # Attempt to set 10s timeout if supported by DDGS, fallback securely
            with DDGS(timeout=10) as ddgs:
                ddg_results = ddgs.text(query, max_results=5)
                if ddg_results:
                    for item in ddg_results:
                        results.append({
                            "url": item.get("href", ""),
                            "title": item.get("title", ""),
                            "content": item.get("body", "")
                        })
        except Exception as e:
            state["error_log"].append(f"DuckDuckGo search error: {str(e)}")

    # Update state based on final outcome
    if results:
        state["search_results"] = results
        state["current_step"] = "search_complete"
    else:
        state["search_results"] = []
        state["current_step"] = "search_failed"
        state["error_log"].append("Both PRIMARY and FALLBACK searches failed or returned empty results.")

    return state
