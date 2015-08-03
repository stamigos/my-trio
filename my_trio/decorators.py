from flask import jsonify
from functools import wraps


def jsonify_result(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        result = func(*args, **kwds)
        return jsonify(result.items())
    return wrapper

