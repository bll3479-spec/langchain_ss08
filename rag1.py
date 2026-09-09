#1. 폴더 안 의 pdf를 읽어서 하나의 docs로 세팅
#pdf라는 폴더 아래 있는 모든 pdf를 읽어서 docs라는 리스트에 내용 추가
import os
from langchain_community.document_loaders import PyPDFLoader
def load_pdfs(path):
    #오류 상황1: 경로가 틀린 경우
    if not path:
        print(f'경로 틀림.')
    #오류 상황2: 폴더에 pdf 없는 경우
    pdf_lists = [os.path.join(path, x) for x in os.listdir(path) if 'pdf' in x]
    if len(pdf_lists) <1:
        #raise: 시스템적인 오류를 일으키거나 알림을 실행.(고의로 표기)
        raise FileNotFoundError(f'{path}에 pdf 존재하지 않음.')

    docs = []
    for pdf in pdf_lists:
        docs.extend(PyPDFLoader(pdf).load())
    print(f'{len(docs)}')
    return docs
#2. docs 청크화
from langchain_text_splitters import RecursiveCharacterTextSplitter
def split_docs(docs, chunk_size = 1000, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    split_docs = splitter.split_documents(docs)
    return split_docs
#3. 청크 벡터화
#Chroma에서 초기 데이터 생성과정
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
#벡터db 종류: faiss, chroma db, BM25?, pinecone, weaviate
def vectorstore(dir, collection):
    return Chroma(collection_name = collection, embedding_function = OpenAIEmbeddings(), persist_directory = dir)

#새로운 문서가 들어왔을 때, split 후 기존 vectordb에 추가
def add_to_vectorstore(vectordb, splits):
    vectordb.add_documents(splits)
    return vectordb


#4. 리트리버
#유사도 검색 후 k개 만큼의 유사 문서를 return
def build_retrieval(vectordb, k):
    return vectordb.as_retriever(serarch_kwargs ={'k':k})


#5. 리트리버 얹은 chain 정의
#리트리버 후 질문
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
def build_rag_chain(chat, retriever):
    prompt = ChatPromptTemplate.from_messages([
        ('human', '''Answer the question using only the context below.
                    Q : {input}
                    C : {context}
                    ''')
    ])
    combine = create_stuff_documents_chain(chat, prompt, document_separator='\n\n')
    return create_retrieval_chain(retriever, combine)

from dotenv import load_dotenv 
load_dotenv()

if __name__ == '__main__':
    #pdf를 특정 장소에 갖고 있는지?
    #갖고 있는 pdf가 vectordb에 있는지?
    vectordb = vectorstore('./vectordb', collection='pdf_docs')
    if len(vectordb.get(limit=1)['ids']) > 0:
        #있다 -> 추가 필요 없음
        print(f'기존 파일 재사용')
    else:
        #없다 -> 추가 필요함
        docs = load_pdfs('./pdfs')
        split_doc = split_docs(docs)
        print(f'{len(docs)} -> {len(split_doc)}개로 나눠짐')
        add_to_vectorstore(vectordb=vectordb, splits = split_doc)
    chat = ChatOpenAI(temperature = 0.7, model='gpt-4o')
    retrieval= build_retrieval(vectordb=vectordb, k=3)
    rag_chain = build_rag_chain(chat, retriever=retrieval)
    question = input('경제 용어를 물어보세요 : \n')
    result = rag_chain.invoke({'input': question, 'context': retrieval })
    print(result)