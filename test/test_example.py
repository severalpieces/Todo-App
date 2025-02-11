import pytest
def test_equal_or_not():
    assert 3==3
    assert 3!=1

def test_is_instance():
    assert isinstance("this is a string", str)
    assert not isinstance("10", int)

def test_boolean():
    validated = True
    assert validated is True
    assert not validated is False
    assert ("hello" == "hi") is False

def test_type():
    assert type("string" is str)
    assert type(10 is int)
    assert type("string" is not int)

def test_greater_or_less_than():
    assert 7 < 10
    assert 4 > 3

def test_list():
    nums_list = [1,2,3,4,5]
    any_list = [False, 0, [], "", None]
    nums_list2 = [0,1,2]
    assert 1 in nums_list
    assert 7 not in nums_list
    assert not 6 in nums_list
    assert all(nums_list)
    assert any(nums_list2)
    assert not all(nums_list2)
    assert not any(any_list)

class Student:
    def __init__(self, first_name: str, last_name: str, major: str, year: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.year = year

@pytest.fixture
def default_employee():
    return Student("John", "Doe", "computer science", 3)

def test_person_initialization(default_employee): # look for a function called default_employee that is a pytest fixture, call the function and pass its return value as a parameter into this current function (dependency injection)
    assert default_employee.first_name == "John", "First name should be John"
    assert default_employee.last_name == "Doe", "Last name should be Doe"
    assert default_employee.major == "computer science"
    assert default_employee.year == 3