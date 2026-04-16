import requests
from urllib.parse import urlparse

try:
    from agent_state import AgentState
except ImportError:
    from typing import Any
    AgentState = Any

def validate_node(state: AgentState) -> AgentState:
    search_results = state.get("search_results", [])
    summaries = state.get("summaries", [])
    
    validation_flags = []
    
    blocked_domains = [
        "twitter.com", "x.com", "reddit.com", 
        "facebook.com", "instagram.com", "tiktok.com"
    ]
    spam_words = [
        "buy now", "click here", "free download", 
        "sign up", "subscribe now", "limited offer"
    ]
    
    for result in search_results:
        url = result.get("url", "")
        content = result.get("content", "")
        title = result.get("title", "")
        
        # CHECK 1: URL reachable
        check1 = False
        if url:
            try:
                response = requests.head(url, timeout=3, allow_redirects=True)
                check1 = response.status_code < 400
            except requests.RequestException:
                check1 = False
                
        # CHECK 2: Content length > 150
        check2 = len(content) > 150
        
        # CHECK 3: Not a blocked domain
        check3 = True
        if url:
            try:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.lower()
                # Check for exact block or subdomain matches
                if any(domain == blocked or domain.endswith(f".{blocked}") for blocked in blocked_domains):
                    check3 = False
            except Exception:
                pass
                
        # CHECK 4: No spam signals in title
        check4 = True
        if title:
            title_lower = title.lower()
            if any(spam in title_lower for spam in spam_words):
                check4 = False
                
        # A source PASSES if it meets at least 3 of 4 checks
        passes = (check1 + check2 + check3 + check4) >= 3
        validation_flags.append(passes)
        
    state["validation_flags"] = validation_flags
    
    # Filter using zip. (Assumes len(summaries) == len(search_results))
    state["validated_summaries"] = [s for s, f in zip(summaries, validation_flags) if f]
    state["validated_sources"] = [r for r, f in zip(search_results, validation_flags) if f]
    
    if len(state["validated_summaries"]) < 2:
        state["current_step"] = "validation_failed"
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        state["refined_query"] = state.get("query", "") + " research paper academic study"
        
        if "error_log" not in state:
            state["error_log"] = []
        state["error_log"].append("Validation Warning: Fewer than 2 validated summaries available.")
    else:
        state["current_step"] = "validation_passed"
        
    return state
