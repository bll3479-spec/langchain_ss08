# 그래프 생김새 정의
# 노드, 엣지 연결
from typing import TypedDict
from langgraph.graph import StateGraph, END


# 그래프 따라다닐 state 정의
class State(TypedDict):
    user_input: str
    location: str
    timeslot: str
    season: str
    weather: str
    intent: str
    recommend_items: list
    search_keywords: str
    recommend_place: dict
    final_message: str


def route_intent(state: State):
    intent = state.get("intent", "")

    if intent == "food":
        return "recommend_food"
    elif intent == "activity":
        return "recommend_activity"
    else:
        return "unexpected"


import nodes


def build_graph():
    # 그래프 따라다닐 상태 세팅
    build = StateGraph(State)

    build.add_node("classify_intent", nodes.classify_intent)
    build.add_node("get_time_slot", nodes.get_time_slot)
    build.add_node("get_season", nodes.get_season)
    build.add_node("get_weather", nodes.get_weather)
    build.add_node("recommend_food", nodes.recommend_food)
    build.add_node("recommend_activity", nodes.recommend_activity)
    build.add_node("generate_search_keyword", nodes.generate_search_keyword)
    build.add_node("search_place", nodes.search_place)
    build.add_node("summarize_output", nodes.summarize_output)
    build.add_node("handle_unsupported", nodes.handle_unsupported)

    # 시작점 정의
    build.set_entry_point("classify_intent")

    build.add_edge("classify_intent", "get_time_slot")
    build.add_edge("get_time_slot", "get_season")
    build.add_edge("get_season", "get_weather")

    build.add_conditional_edges(
        "get_weather",
        route_intent,
        {
            "unexpected": "handle_unsupported",
            "recommend_activity": "recommend_activity",
            "recommend_food": "recommend_food",
        },
    )
    build.add_edge("handle_unsupported", END)

    build.add_edge("recommend_activity", "generate_search_keyword")
    build.add_edge("recommend_food", "generate_search_keyword")

    build.add_edge("generate_search_keyword", "search_place")
    build.add_edge("search_place", "summarize_output")
    build.add_edge("summarize_output", END)

    return build.compile()
