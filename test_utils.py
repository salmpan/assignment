"""Unit tests for miscellaneus utilities"""
from utils import remove_common_elements_from_list, fetch_ids_from_urls


def test_remove_common_elements_from_list1():
    """Should remove all items from list2 which are included in list1"""
    list1 = [1, 2, 4, 6, 8]
    list2 = []

    result = remove_common_elements_from_list(list1, list2)
    result.sort()
    assert result == [1, 2, 4, 6, 8]


def test_remove_common_elements_from_list2():
    """Should remove all items from list2 which are included in list1"""
    list1 = [1, 2, 4, 6, 8]
    list2 = [2, 6, 8, 20, 5]

    result = remove_common_elements_from_list(list1, list2)
    result.sort()
    assert result == [1, 4]


def test_fetch_ids_from_urls1():
    """Should return a list of ids from given URLs"""
    films = [
        'https://swapi.py4e.com/api/films/1/', 
        'https://swapi.py4e.com/api/films/2/', 
        'https://swapi.py4e.com/api/films/3/', 
        'https://swapi.py4e.com/api/films/6/', 
        'https://swapi.py4e.com/api/films/7/'
    ]

    result = list(fetch_ids_from_urls(films))
    result.sort()
    assert result == [1, 2, 3, 6, 7]
