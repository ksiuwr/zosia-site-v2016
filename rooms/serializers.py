from django.shortcuts import reverse
from django.forms.models import model_to_dict


def room_to_dict(room):
    model = model_to_dict(room)
    model['join'] = reverse('rooms_join', kwargs={'room_id': room.pk})
    model['is_locked'] = room.is_locked
    model['free_places'] = room.capacity - room.users.count()
    model.pop('users')
    return model

def user_to_dict(user):
    name = user.username
    if user.first_name or user.last_name:
        name = "{} {}".format(user.first_name, user.last_name)
    dic = {
        'name': name
    }

    return dic
