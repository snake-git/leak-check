from typing import Optional, List

from pydantic import BaseModel


class ModelResponseSource(BaseModel):
    id: int
    source: Optional[str]

class ModelResponsePerson(BaseModel):
    id: Optional[str]
    name: Optional[str]
    receiver: Optional[str]
    nickname: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    car: Optional[str]
    email: Optional[str]
    qq: Optional[int]
    weibo: Optional[int]
    contact:Optional[str]
    company: Optional[str]
    source: Optional[str]

class ModelResponsePersonAggregated(BaseModel):
    id: List[str]
    name: List[str]
    receiver: List[str]
    nickname: List[str]
    phone: List[str]
    address: List[str]
    car: List[str]
    email: List[str]
    qq: List[int]
    weibo: List[int]
    contact: List[str]
    company: List[str]
    source: List[str]