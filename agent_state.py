from typing import TypedDict, List, Dict

class AgentState(TypedDict):
    query: str # original user research question
    refined_query: str # optionally modified query on retry
    search_results: List[Dict] # each: { url, title, content }
    summaries: List[str] # one summary per search result
    validation_flags: List[bool] # True if source passed quality check
    validated_summaries: List[str] # only summaries where flag is True
    validated_sources: List[Dict] # only sources where flag is True
    final_report: Dict # structured report output
    current_step: str # for UI: "searching" | "summarizing" | "validating" | "reporting" | "done" | "error"
    error_log: List[str] # captures non-fatal errors gracefully
    iteration_count: int # retry counter, max 3
    llm_used: List[str] # track which LLM was used

def create_initial_state(query: str) -> AgentState:
    return {
        "query": query,
        "refined_query": "",
        "search_results": [],
        "summaries": [],
        "validation_flags": [],
        "validated_summaries": [],
        "validated_sources": [],
        "final_report": {},
        "current_step": "searching",
        "error_log": [],
        "iteration_count": 0,
        "llm_used": []
    }
