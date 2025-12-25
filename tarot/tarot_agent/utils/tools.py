"""

타로 그래프 도구들 (@tool 데코레이터 함수들)

"""

from langchain_core.tools import tool

from ..utils.translation import translate_korean_to_english_with_llm

from ..utils.helpers import convert_numpy_types

from Fortune.tarot.tarot_rag_system import TarotRAGSystem

rag_system = None

def initialize_rag_system():
    """RAG 시스템 초기화"""
    global rag_system
    if rag_system is None:
        rag_system = TarotRAGSystem(
            card_faiss_path="tarot_card_faiss_index",
            spread_faiss_path="tarot_spread_faiss_index"
        )
        print("✅ RAG 시스템 초기화 완료")
@tool

def search_tarot_spreads(query: str) -> str:
    """타로 스프레드를 검색합니다 - LLM 번역 사용"""
    if rag_system is None:
        return "RAG 시스템이 초기화되지 않았습니다."
    try:
        english_query = translate_korean_to_english_with_llm(query)
        results = rag_system.search_spreads(english_query, final_k=3)
        safe_results = convert_numpy_types(results)
        print(f"🔮 SPREAD SEARCH: {query} -> {english_query}")
        print(f"🔍 검색 결과: {len(safe_results)}개")
        return str(safe_results)
    except Exception as e:
        return f"스프레드 검색 중 오류가 발생했습니다: {str(e)}"
@tool

def search_tarot_cards(query: str) -> str:
    """타로 카드의 의미를 검색합니다 - LLM 번역 사용"""
    if rag_system is None:
        return "RAG 시스템이 초기화되지 않았습니다."
    try:
        english_query = translate_korean_to_english_with_llm(query)
        results = rag_system.search_cards(english_query, final_k=5)
        safe_results = convert_numpy_types(results)
        print(f"🃏 CARD SEARCH: {query} -> {english_query}")
        print(f"🔍 검색 결과: {len(safe_results)}개")
        return str(safe_results)
    except Exception as e:
        return f"카드 검색 중 오류가 발생했습니다: {str(e)}"
