from pydantic import BaseModel
from src.utils.models import set_field_values, Pagination, PaginatedResponse
from datetime import date

class MockData(BaseModel):
    name: str
    age: int

class MockObj:
    def __init__(self, name=None, age=None):
        self.name = name
        self.age = age

def test_set_field_values_pydantic():
    data = MockData(name="John", age=30)
    obj = MockObj()
    
    set_field_values(obj, data)
    
    assert obj.name == "John"
    assert obj.age == 30

def test_set_field_values_dict():
    data = {"name": "Jane", "age": 25}
    obj = MockObj()
    
    set_field_values(obj, data)
    
    assert obj.name == "Jane"
    assert obj.age == 25

def test_pagination_defaults():
    p = Pagination(page=1, size=20, all=False, start_date=str(date.today()), end_date=str(date.today()))
    assert p.page == 1
    assert p.size == 20
    assert p.skip == 0
    assert p.limit == 20
    assert p.all is False
    assert p.start_date == str(date.today())
    assert p.end_date == str(date.today())
    assert p.query is None

def test_pagination_custom():
    p = Pagination(page=2, size=10, all=True, start_date="2023-01-01", end_date="2023-12-31", query="test")
    assert p.page == 2
    assert p.size == 10
    assert p.skip == 10
    assert p.limit == 10
    assert p.all is True
    assert p.start_date == "2023-01-01"
    assert p.end_date == "2023-12-31"
    assert p.query == "test"

def test_paginated_response():
    p = Pagination(page=1, size=2, all=False, start_date="2023-01-01", end_date="2023-01-01")
    data = ["item1", "item2"]
    total = 10
    
    response = PaginatedResponse[str].from_pagination(p, data, total)
    
    assert response.page == 1
    assert response.size == 2
    assert response.data == data
    assert response.total == total
    assert response.start_date == p.start_date
    assert response.end_date == p.end_date
