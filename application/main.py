# 1. langgraph로 그래프 빌드
# 2. 요청을 인풋 받아 실행

from graph import build_graph

graph = build_graph()

if __name__ == "__main__":
    print(
        "저는 지도 기반 장소 추천 서비스입니다. 사용자의 위치나 상황에 따라 장소를 추천해드려요."
    )
    location = input("지금 어디에 계시나요? \n")
    user_input = input("지금 기분이나 상황을 알려주세요.")

    # node.py에서 state:dict
    state = {"location": location, "user_input": user_input, "intent": "food"}
    for e in graph.stream(state):
        print(e)
