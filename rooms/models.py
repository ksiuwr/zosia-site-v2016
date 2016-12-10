from datetime import datetime, timedelta

from django.db import models, transaction

from users.models import User
from conferences.models import Zosia


class RoomLock(models.Model):
    # 3 hours
    TIMEOUT = timedelta(0, 3*3600)

    expiration_date = models.DateTimeField()
    password = models.CharField(max_length=4)

    @classmethod
    def make(cls, room, user):
        return cls.objects.create(room=room,
                                  user=user,
                                  expiration_date=datetime.now() + cls.TIMEOUT)

    @property
    def is_expired(self):
        return self.expiration_date < datetime.now()

    def unlocks(self, password):
        return self.password == password


class Room(models.Model):
    name = models.CharField(
        max_length=300)
    description = models.TextField(
        default='')
    capacity = models.IntegerField()
    zosia = models.ForeignKey(Zosia)

    lock = models.ForeignKey(RoomLock, blank=True, null=True)

    @property
    def free_places(self):
        return self.capacity - self.userroom_set.count()

    @property
    def is_locked(self):
        return self.lock and not self.lock.is_expired

    @transaction.atomic
    def join(self, user, password=''):
        if is_locked and not self.lock.unlocks(password):
            return None

        if not self.lock or self.lock.is_expired:
            self.lock = RoomLock.make(self, user)

        return UserRoom.objects.create(room=self, user=user)


class UserRoom(models.Model):
    room = models.ForeignKey(Room)
    user = models.ForeignKey(User)
