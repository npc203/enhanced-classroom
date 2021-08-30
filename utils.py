# Metaclass for singleton classes
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def search(data, search_key, search_value):
    """
    Search for a string in the given dictionary.
    """
    for key, data_val in data.items():
        if data_val[search_key] == search_value:
            return key
    raise RuntimeError("No such data found")
