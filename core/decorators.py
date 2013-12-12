from django.utils.decorators import available_attrs
from functools import wraps


def ssl_exempt(view_func):
    """
    Marks a view function as being exempt from SSL.
    """
    # We could just do view_func.csrf_exempt = True, but decorators
    # are nicer if they don't have side-effects, so we return a new
    # function.
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.ssl_exempt = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
