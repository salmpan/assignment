"""Miscellaneous utilities"""

def remove_common_elements_from_list(list1: list, list2: list):
    """Removes from list1 elements included in list2.
    Elements are supposed to be unique.
    """
    return list(set(list1).difference(set(list2)))


def fetch_ids_from_urls(urls: list):
    """Gets the Star Wars API ids from a list of URL.
    The Id is the last element in the URL"""
    return map(lambda l: int(l.strip('/').rsplit('/', 1)[-1]), urls)
