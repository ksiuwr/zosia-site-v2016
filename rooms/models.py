import random
import string
from datetime import timedelta

from django.utils import timezone
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from users.models import User
from conferences.models import Zosia


def random_string(length=10):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


class RoomLock(models.Model):
    # 3 hours
    TIMEOUT = timedelta(0, 3*3600)

    expiration_date = models.DateTimeField()
    password = models.CharField(max_length=4)

    user = models.ForeignKey(User)

    @classmethod
    def make(cls, user, expiration=None):
        expiration = expiration or cls.TIMEOUT
        return cls.objects.create(user=user,
                                  password=random_string(4),
                                  expiration_date=timezone.now() + expiration)

    @property
    def is_expired(self):
        return self.expiration_date < timezone.now()

    def unlocks(self, password):
        return self.password == password

    def owns(self, user):
        return self.user == user


class Room(models.Model):
    name = models.CharField(
        max_length=300)
    description = models.TextField(
        default='')
    capacity = models.IntegerField()
    zosia = models.ForeignKey(Zosia)

    lock = models.ForeignKey(RoomLock,
                             on_delete=models.SET_NULL,
                             blank=True,
                             null=True)

    @property
    def free_places(self):
        return self.capacity - self.userroom_set.count()

    @property
    def is_locked(self):
        return self.lock and not self.lock.is_expired

    @transaction.atomic
    def join(self, user, password='', expiration=None):
        if self.is_locked and not self.lock.unlocks(password):
            return ValidationError(_('Cannot join room %(room), is locked.'),
                                   code='invalid',
                                   params={
                                       'room': self
                                   })

        # Ensure room is not full
        if self.userroom_set.count() >= self.capacity:
            return ValidationError(_('Cannot join room %(room), is full.'),
                                   code='invalid',
                                   params={
                                       'room': self
                                   })

        # Remove user from previous rooms
        prev_userroom = user.userroom_set.select_related('room').filter(room__zosia=self.zosia).first()
        if prev_userroom:
            if prev_userroom.room.is_locked:
                prev_userroom.room.lock.delete()
            prev_userroom.delete()

        owner_lock = None
        if not self.lock or self.lock.is_expired:
            owner_lock = RoomLock.make(user, expiration=expiration)
            self.lock = owner_lock

        self.save()
        return UserRoom.objects.create(room=self, user=user)

    @transaction.atomic
    def unlock(self, user):
        if self.is_locked and self.lock.owns(user):
            self.lock.delete()


class UserRoom(models.Model):
    room = models.ForeignKey(Room)
    user = models.ForeignKey(User)
