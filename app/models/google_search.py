from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class URL(BaseModel):
    """Google搜索URL模板信息"""
    type: str
    template: str


class Query(BaseModel):
    """查询信息"""
    title: str
    totalResults: str
    searchTerms: str
    count: int
    startIndex: int
    inputEncoding: str
    outputEncoding: str
    safe: str
    cx: str


class Context(BaseModel):
    """搜索上下文"""
    title: str


class SearchInformation(BaseModel):
    """搜索结果信息"""
    searchTime: float
    formattedSearchTime: str
    totalResults: str
    formattedTotalResults: str


class PageMap(BaseModel):
    """页面映射信息，包含问题、回答和人物等数据"""
    question: Optional[List[Dict[str, Any]]] = None
    answer: Optional[List[Dict[str, Any]]] = None
    person: Optional[List[Dict[str, Any]]] = None
    metatags: Optional[List[Dict[str, Any]]] = None


class SearchResultItem(BaseModel):
    kind: str
    title: str
    htmlTitle: str
    link: str
    displayLink: str
    snippet: Optional[str] = None
    htmlSnippet: Optional[str] = None
    formattedUrl: str
    htmlFormattedUrl: str
    pagemap: Optional[PageMap] = None


class GoogleSearchResult(BaseModel):
    kind: str
    url: URL
    queries: Dict[str, List[Query]]
    context: Context
    searchInformation: SearchInformation
    items: List[SearchResultItem]