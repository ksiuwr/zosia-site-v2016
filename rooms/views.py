from django.shortcuts import render


# GET
# Cache
def rooming(request):
    # Return HTML w/ rooms layout
    pass


# GET
# Don't cache
def rooms(request):
    # Ajax
    # Return JSON view of rooms
    pass


# POST
def join(request):
    # Ajax
    # Try to join given room
    pass
