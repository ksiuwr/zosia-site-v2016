from functools import wraps

from django.shortcuts import redirect


def anonymous_required(view):
    @wraps(view)
    def func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return view(request, *args, **kwargs)

    return func
