#의존성 검사, 병렬실행
#의존성이 없는 노드끼리는 실제로 스레드로 동시에 실행

from dotenv import load_dotenv
load_dotenv()

import json, time
from concurrent.futures import ThreadPoolExecutor   #병렬실행
from openai import OpenAI
client = OpenAI()

#client와 소통(채팅 입력 -> 답변 반환)
def generate(prompt, temperature=0.7):
    completion = client.chat.completions.create(
        model = 'gpt-4o',
        temperature= 0.7, 
        messages= [{'role': 'user', 'content':prompt}]
    )
    return completion.choices[0].message.content
#아웃풋 다듬기
def extract_json_from_text(response):
    if not response:
        return None
    text = response
    if response.startswith('```'):
        text = response.split('```')[1]
        if text.startswith('json'):
            text = text[4:]
    text = text.strip()
    #리스트에 대비
    if text.startswith('['):
        open_t, close_t = '[', ']'
    else:
        open_t, close_t = '{', '}'
    start, end = text.find(open_t), text.rfind(close_t)
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end+1])
    except json.JSONDecodeError:
        return None


#나온 plan을 갖고 의존성 그래프 생성 -> 노드(함수)마다 id를 가짐
#depends_one -> 비어 있으면 개별적으로 수행가능한 독립적인 일
#그래프 생성
def create_depend_graph(goal, max_result = 3):
    prompt = f'''
        다음 목표를 달성하기 위해 실행 그래플르 만드시오.
        Json만 출력하고,
        서로 관계 없는 작업은 depends_on이라는 요소를 비워두고,
        앞 작업의 결과가 필요한 작업은 depends_one에 그 작업의 id를 적어주세요.
        
        형식: {{"nodes": [
            {{"id": "1", "action": "경쟁사_조사", "depends_on": []}},
            {{"id": "2", "action": "시장_조사", "depends_on": []}},
            {{"id": "3", "action": "초안_작성", "depends_on": ["1", "2"]}}
            ]}}

        목표: {goal}

        JSON만 출력:
        '''

    for attempts in range(max_result):
        response = generate(prompt)
        graph = extract_json_from_text(response)
        #그래프라는 객체가 존재하고 / graph.get(): 그래프가 리스트인지 확인하고 그 안에 'nodes'가 존재하는지 / nodes의 값이 존재하는지?
        if graph and isinstance(graph.get('nodes'), list) and graph['nodes']:
            return graph
        print(f'재시도 중... {attempts+1}/{max_result}')
    return None

#병렬적인 그래프 실행
def execute_graph(graph):
    #노드 내에 있는 리스트를 가져올 것(리스트 내의 것 = n(내용 덩어리), n의 id(1,2,3...)를 가져옴)
    #1:{id_1의 내용~} 형태로 저장됨.
    nodes = {n['id']: n for n in graph['nodes']}
    done = set()        #마친 일
    results = []        #마친 결과

    section = 1         #한 덩어리의 묶음 실행 (의존성이 없는 병렬실행 가능 단위)
    #마친 일의 길이가 노드의 일의 길이보다 작음 = 일이 남아있음. 그동안 while 반복
    while len(done) < len(nodes):
        #nodes.items() -> 딕셔너리, nid(keys), n(values)
        ready = [n for nid, n in nodes.items()
                 #nid not in done = 마치지 않은 nid, 해야하는 일을 가져올 것
                 #depends_on을 갖고 있으면 ready에 넣기
                 if nid not in done and all(d in done for d in n.get('depends_on', []))]
        #ready가 없으면(할 일이 없음 / depends_on이 없는 노드만 남았음)
        if not ready:
            print(f'더 이상 실행가능한 노드가 없음(검증되지 않음)')
            break
        print(f'섹션 {section} 동시 실행: {[n['action'] for n in ready]}')
        #지금 task를 할 때 시간을 기록
        t0 = time.time()
        #스레드(병렬) 실행. 어떻게? len(ready)만큼
        with ThreadPoolExecutor(max_workers=len(ready)) as executor:
            #map -> 순환 가능한 구성요소에 동일한 적용
            #n에 action을 넣고 ready와 함께 run_action
            outputs = list(executor.map(lambda n : run_action(n['action']), ready))
        #현재 시간 - 시작시간 = 걸린 시간
        elapsed = time.time() - t0
        print(f'elapsed 걸린 시간: {elapsed}')
        for n, out in zip(ready, outputs):
            results.append({'id':n['id'], 'action':n['action'], 'result':out})
            done.add(n['id'])
        section += 1
    return results
#여기서는 더미 실제로는 돌아가는 코드 넣기 (agent 넣어서 섹션별로 돌리기)
def run_action(action):
    time.sleep(1)
    return f'{action} 완료'





if __name__ == '__main__':
    query = input('무엇을 하고 싶은지 알려주세요.: \n')
    #query 기반 작업 생성 -> result
    result = create_depend_graph(query)
    #r = {덩어리 하나}
    #for r in result['nodes']:
    response = execute_graph(result)
    print(f'response : {response}')