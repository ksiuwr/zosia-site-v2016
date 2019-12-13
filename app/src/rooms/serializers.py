from django.forms.models import model_to_dict


def room_to_dict(room):
    model = model_to_dict(room)
    model['capacity'] = room.capacity
    model['is_locked'] = room.is_locked
    model['free_places'] = room.capacity - room.members.count()
    model.pop('members')

    return model


def user_to_dict(user):
    name = user.full_name
    dic = {'name': name}

    return dic
