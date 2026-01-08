from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, StateGraph, START
from app.vectorstore import get_retriever

# --- State 정의 ---
class GraphState(TypedDict):
    question: str
    generation: str
    documents: list

# --- Nodes ---

def retrieve(state: GraphState):
    """
    질문에 관련된 문서를 검색합니다.
    """
    print("--- RETRIEVE ---")
    question = state["question"]
    retriever = get_retriever()
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

def generate(state: GraphState):
    """
    검색된 문서를 바탕으로 답변을 생성합니다.
    """
    print("--- GENERATE ---")
    question = state["question"]
    documents = state["documents"]
    
    # LLM 설정
    llm = ChatOpenAI(model="gpt-4o", temperature=0) # 최신 트렌드 반영
    
    # 프롬프트
    prompt = ChatPromptTemplate.from_template(
        """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
        
        Question: {question} 
        Context: {context} 
        Answer:"""
    )
    
    # 체인 구성
    rag_chain = prompt | llm | StrOutputParser()
    
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"generation": generation}

# --- Graph 구성 ---

workflow = StateGraph(GraphState)

# 노드 추가
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

# 엣지 연결
workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# 컴파일
app_graph = workflow.compile()
