#질문을 할 때, 질문 답변에 참고할 자료를 미리 셋팅 -> 자료를 찾아 같이 전달
#Retrieval Augmented Generation(검색, 증강, 생성)]
#유사도 검색-> 1. vectorDB 이용 or 2. TF-IDF 이용
#Retrieval.vector DB: 검색에 필요한 문장을 임베딩, 비슷한 문장을 분류해놓고 유사도 검색
#augmented.알고리즘: 알고리즘 이용해서 유사도 검색

from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retriever_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

def bulid_rag_chain(llm, retriever, document_sep = '\n\n'):
    prompt = ChatPromptTemplate.from_message([
    ('human', '''Answer the question using only the context below. \n\n 
        {context}\n\n 
        question : {input}''')])

    combine = create_stuff_documents_chain(llm, prompt, document_seperator = document_sep)
    return create_retriever_chain(retriever, combine)