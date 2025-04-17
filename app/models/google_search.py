from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, root_validator

class URL(BaseModel):
    type: Optional[str] = ""
    template: Optional[str] = ""
    
    class Config:
        extra = "ignore"

class Query(BaseModel):
    title: Optional[str] = ""
    totalResults: Optional[str] = "0"
    searchTerms: Optional[str] = ""
    count: Optional[int] = 0
    startIndex: Optional[int] = 0
    inputEncoding: Optional[str] = ""
    outputEncoding: Optional[str] = ""
    safe: Optional[str] = ""
    cx: Optional[str] = ""
    
    class Config:
        extra = "ignore"

class Context(BaseModel):
    title: Optional[str] = ""
    
    class Config:
        extra = "ignore"

class SearchInformation(BaseModel):
    searchTime: Optional[float] = 0.0
    formattedSearchTime: Optional[str] = ""
    totalResults: Optional[str] = "0"
    formattedTotalResults: Optional[str] = "0"
    
    class Config:
        extra = "ignore"

class PageMap(BaseModel):
    question: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    answer: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    person: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    metatags: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    
    class Config:
        extra = "ignore"

class SearchResultItem(BaseModel):
    kind: Optional[str] = ""
    title: Optional[str] = ""
    htmlTitle: Optional[str] = ""
    link: Optional[str] = ""
    displayLink: Optional[str] = ""
    snippet: Optional[str] = None
    htmlSnippet: Optional[str] = None
    formattedUrl: Optional[str] = ""
    htmlFormattedUrl: Optional[str] = ""
    pagemap: Optional[PageMap] = None
    
    class Config:
        extra = "ignore"

class GoogleSearchResult(BaseModel):
    kind: Optional[str] = ""
    url: Optional[URL] = None
    queries: Optional[Dict[str, List[Query]]] = Field(default_factory=dict)
    context: Optional[Context] = None
    searchInformation: Optional[SearchInformation] = None
    items: Optional[List[SearchResultItem]] = Field(default_factory=list)
    
    @root_validator(pre=True)
    def ensure_required_fields(cls, values):
        if values.get("url") is None:
            values["url"] = {"type": "", "template": ""}
        
        if values.get("queries") is None:
            values["queries"] = {}
            
        if values.get("context") is None:
            values["context"] = {"title": ""}
            
        if values.get("searchInformation") is None:
            values["searchInformation"] = {
                "searchTime": 0.0,
                "formattedSearchTime": "",
                "totalResults": "0",
                "formattedTotalResults": "0"
            }
            
        if values.get("items") is None:
            values["items"] = []
            
        return values
    
    class Config:
        extra = "ignore"