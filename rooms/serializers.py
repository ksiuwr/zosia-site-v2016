from django.shortcuts import reverse
from django.forms.models import model_to_dict

def room_to_dict(room):
    model = model_to_dict(room)
    model['join'] = reverse('rooms_join', kwargs={'room_id': room.pk})
    model['free_places'] = room.free_places
    model['is_locked'] = room.is_locked
    return model
