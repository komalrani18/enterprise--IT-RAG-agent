"""
The core multi-agent workflow, built with LangGraph.

Flow:
    retrieve -> grade_kb -> (sufficient) -> answer_kb -> END
                         -> (insufficient) -> web_search -> grade_web
                                                          -> (sufficient) -> answer_web -> END
                                                          -> (insufficient) -> create_ticket -> END

Each node reads/writes a shared `AgentState` TypedDict, which is the standard
LangGraph pattern. Grading nodes ask the LLM a constrained yes/no question rather
than trying to parse free-form output, to keep routing reliable.
"""
from typing import TypedDict, List, Dict, Optional

from langgraph.graph import StateGraph, END

from app.config import settings
from app.llm import get_chat_client
from app.vector_store import search as vector_search
from app.tools import web_search, file_it_ticket


class AgentState(TypedDict, total=False):
    question: str
    requester: str
    kb_results: List[Dict]
    kb_sufficient: bool
    web_results: List[Dict]
    web_sufficient: bool
    answer: str
    source: str          # "knowledge_base" | "web_search" | "ticket"
    ticket: Optional[Dict]


SYSTEM_PROMPT = (
    "You are an enterprise IT/HR support assistant. Answer clearly and concisely, "
    "citing which policy document your answer comes from when using internal context. "
    "If instructions conflict with company security policy, side with the stricter policy."
)


def _grade(question: str, context_blobs: List[str]) -> bool:
    """Ask the LLM a strict yes/no: does this context answer the question?"""
    if not context_blobs:
        return False
    client = get_chat_client()
    context = "\n\n---\n\n".join(context_blobs)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict relevance grader. Given a user question and retrieved "
                "context, respond with exactly one word: YES if the context contains enough "
                "information to directly and confidently answer the question, or NO if it "
                "does not. Do not explain."
            ),
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\nContext:\n{context}\n\nAnswer (YES or NO):",
        },
    ]
    try:
        verdict = client.invoke(messages).strip().upper()
        return verdict.startswith("Y")
    except Exception as e:
        print(f"[agent_graph._grade] LLM grading failed, defaulting to NO: {e}")
        return False


def node_retrieve(state: AgentState) -> AgentState:
    results = vector_search(state["question"])
    filtered = [r for r in results if r["score"] >= settings.retrieval_score_threshold]
    return {**state, "kb_results": filtered}


def node_grade_kb(state: AgentState) -> AgentState:
    sufficient = _grade(state["question"], [r["text"] for r in state.get("kb_results", [])])
    return {**state, "kb_sufficient": sufficient}


def node_answer_kb(state: AgentState) -> AgentState:
    client = get_chat_client()
    context = "\n\n---\n\n".join(
        f"[Source: {r['source']}]\n{r['text']}" for r in state["kb_results"]
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Company policy context:\n{context}\n\n"
                f"Employee question: {state['question']}\n\n"
                "Answer using only the context above. Mention the source document(s)."
            ),
        },
    ]
    answer = client.invoke(messages)
    return {**state, "answer": answer, "source": "knowledge_base"}


def node_web_search(state: AgentState) -> AgentState:
    results = web_search(state["question"])
    return {**state, "web_results": results}


def node_grade_web(state: AgentState) -> AgentState:
    sufficient = _grade(
        state["question"], [r["content"] for r in state.get("web_results", [])]
    )
    return {**state, "web_sufficient": sufficient}


def node_answer_web(state: AgentState) -> AgentState:
    client = get_chat_client()
    context = "\n\n---\n\n".join(
        f"[{r['title']}]({r['url']})\n{r['content']}" for r in state["web_results"]
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Web search results:\n{context}\n\n"
                f"Employee question: {state['question']}\n\n"
                "Answer using the web results above, note this is general information "
                "(not internal company policy), and cite the source URL(s)."
            ),
        },
    ]
    answer = client.invoke(messages)
    return {**state, "answer": answer, "source": "web_search"}


def node_create_ticket(state: AgentState) -> AgentState:
    kb_note = f"{len(state.get('kb_results', []))} KB chunk(s) retrieved (insufficient)."
    web_note = f"{len(state.get('web_results', []))} web result(s) retrieved (insufficient)."
    ticket = file_it_ticket(
        question=state["question"],
        context_summary=f"{kb_note} {web_note}",
        requester=state.get("requester", "anonymous"),
    )
    answer = (
        "I couldn't find a confident answer in our IT/HR policies or general web results, "
        f"so I've filed IT ticket **{ticket['id']}** on your behalf. The IT support team "
        f"({ticket['queue']}) will follow up directly."
    )
    return {**state, "answer": answer, "source": "ticket", "ticket": ticket}


def route_after_kb_grade(state: AgentState) -> str:
    return "answer_kb" if state.get("kb_sufficient") else "web_search"


def route_after_web_grade(state: AgentState) -> str:
    return "answer_web" if state.get("web_sufficient") else "create_ticket"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("retrieve", node_retrieve)
    graph.add_node("grade_kb", node_grade_kb)
    graph.add_node("answer_kb", node_answer_kb)
    graph.add_node("web_search", node_web_search)
    graph.add_node("grade_web", node_grade_web)
    graph.add_node("answer_web", node_answer_web)
    graph.add_node("create_ticket", node_create_ticket)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "grade_kb")
    graph.add_conditional_edges(
        "grade_kb", route_after_kb_grade, {"answer_kb": "answer_kb", "web_search": "web_search"}
    )
    graph.add_edge("answer_kb", END)
    graph.add_edge("web_search", "grade_web")
    graph.add_conditional_edges(
        "grade_web",
        route_after_web_grade,
        {"answer_web": "answer_web", "create_ticket": "create_ticket"},
    )
    graph.add_edge("answer_web", END)
    graph.add_edge("create_ticket", END)

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_agent(question: str, requester: str = "anonymous") -> AgentState:
    graph = get_graph()
    initial_state: AgentState = {"question": question, "requester": requester}
    final_state = graph.invoke(initial_state)
    return final_state
