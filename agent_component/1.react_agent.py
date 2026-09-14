#re-act 패턴의 에이전틱 AI 구성
from dotenv import load_dotenv
load_dotenv()

import re
from openai import OpenAI       #openai에게 직접 통신 요청
client = OpenAI()

# LLM에게 Thought/Action/Observation 형식을 지시한다
SYSTEM_PROMPT = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer.
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary.

average_dog_weight:
e.g. average_dog_weight: Collie
Returns average weight of a dog when given the breed.

Example session:

Question: How much does a Bulldog weigh?
Thought: I should look the dog's weight using average_dog_weight
Action: average_dog_weight: Bulldog
PAUSE

You will be called again with this:

Observation: A Bulldog weighs 51 lbs

You then output:

Answer: A Bulldog weighs 51 lbs
""".strip()
#model, tool, memory
#세션 -> 랭체인 없이 만드는 경량 에이전트 구조
class Agent:
    def __init__(self, system):
        self.system = system            #페르소나(temperature)
        self.messages = []              #주고 받은 채팅
        if self.system:                 #role: system과 user 등등. 여기서는 system(ai) 누구에게 말하는지, #content: 무슨 내용인지
            self.messages.append({'role': 'system', 'content': system})
    #실제 대화를 주고 받는 동작
    def __call__(self, message):
        self.messages.append({'role':'user', 'content':message})        #내 지시
        result = self.execute()         #ai의 내 지시에 대한 답
        #system(ai 초기 설정), user(사용자 요청), assistant(ai 답변)
        self.messages.append({'role':'assistant', 'content': result})        #그 답에 대한 내 응답
        return result 

    def execute(self):
        completion = client.chat.completions.create(
            model = 'gpt-4o',
            temperature= 0.5,
            messages= self.messages
        )
        return completion.choices[0].message.content        #ai의 답변 중 인간이 이해할 수 있는 것만 추출.


#tool(agent가 활용 가능한 함수, api)
def calculate(what):
    #eval -> 문자를 수학식으로 해석해서 계산해주는 파이썬 내장 함수
    return eval(what)


def average_dog_weight(name):
    if "Scottish Terrier" in name:
        return "Scottish Terriers average 20 lbs"
    elif "Border Collie" in name:
        return "a Border Collie's average weight is 37 lbs"
    elif "Toy Poodle" in name:
        return "a Toy Poodle's average weight is 7 lbs"
    else:
        return "An average dog weighs 50 lbs"


known_actions = {'calculate':calculate, 'average_dog_weight':average_dog_weight}



#실제 실행
#(r'^Action: -> Action: 으로 시작하는 문자열 찾기 (^ = starts with)
#  (\w+) -> \w 문자, + -> 1개 이상                  #Action:으로 시작하는데 문자인 경우
# (.*)$') -> .*(모든 문자, 0개 이상의 값), $ -> 마침표. 줄 끝까지 매칭 
action_re = re.compile(r'^Action: (\w+): (.*)$')


def query(question, max_turns = 5):
    i = 0
    bot = Agent(SYSTEM_PROMPT)
    next_prompt = question
    while i < max_turns:
        i +=1
        result = bot(next_prompt)           #gpt 생성 답
        print(result)
        actions = [action_re.match(line) for line in result.split('\n')
                   if action_re.match(line)]

        if actions:
            action, action_input = actions[0].groups()      #(\w+): (.*)$' 두 그룹이니 두 개로 받고 (액션(함수)/인풋(들어오는 수, 값))
            if action not in known_actions:
                raise Exception(f'unknown action : {action} - {action_input}')
            print(f'running... {action}({action_input})')
            observation = known_actions[action](action_input)

            print(f'observation ... {observation}')
            next_prompt = f'Observation: {observation}'

        else:
            return

if __name__ == '__main__':
    question = '''I have 2 dogs, a border collie and a scottish terrier.
            What is their combined weight?'''

    query(question=question)