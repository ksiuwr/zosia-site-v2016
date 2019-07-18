import random
import string
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from conferences.models import Zosia
from users.models import User


def random_string(length=10):
    return ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(length))


class RoomLockManager(models.Manager):
    # 3 hours
    TIMEOUT = timedelta(0, 3 * 3600)

    def make(self, user, expiration=None):
        expiration = expiration or self.TIMEOUT

        return self.create(user=user,
                           password=random_string(4),
                           expiration_date=timezone.now() + expiration)


class RoomLock(models.Model):
    objects = RoomLockManager()

    expiration_date = models.DateTimeField()
    password = models.CharField(max_length=4)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def is_expired(self):
        return self.expiration_date < timezone.now()

    def unlocks(self, password):
        return self.password == password

    def owns(self, user):
        return self.user == user


class RoomBeds(models.Model):
    single = models.IntegerField(default=0)
    double = models.IntegerField(default=0)
    other = models.IntegerField(default=0)

    @property
    def capacity(self):
        return self.single + 2 * self.double + self.other


class RoomManager(models.Manager):
    def for_zosia(self, zosia, **params):
        defaults = {'zosia': zosia}
        defaults.update(**params)

        return self.filter(**defaults)

    def visible_for_zosia(self, zosia, **params):
        return self.for_zosia(zosia, hidden=False, **params)


class Room(models.Model):
    objects = RoomManager()

    name = models.CharField(max_length=300)
    description = models.TextField(default='')
    hidden = models.BooleanField(default=False)

    zosia = models.ForeignKey(Zosia, on_delete=models.CASCADE)
    beds = models.OneToOneField(RoomBeds, related_name='actual_beds', on_delete=models.CASCADE,
                                blank=True, null=True)
    available_beds = models.OneToOneField(RoomBeds, related_name='available_beds',
                                          on_delete=models.CASCADE, blank=True, null=True)
    lock = models.ForeignKey(RoomLock, on_delete=models.SET_NULL, blank=True, null=True)

    members = models.ManyToManyField(User, through='UserRoom', related_name='room_of_user')

    @property
    def capacity(self):
        return self.available_beds.capacity

    @property
    def is_locked(self):
        return self.lock and not self.lock.is_expired

    @property
    def is_occupied(self):
        return self.members.count()

    @property
    def occupants(self):
        return ", ".join(map(str, self.members.all()))

    @transaction.atomic
    def join(self, user, password='', expiration=None, lock=True):
        if self.is_locked and not self.lock.unlocks(password):
            return ValidationError(_('Cannot join room %(room), is locked.'),
                                   code='invalid',
                                   params={'room': self})

        # Ensure room is not full
        if self.is_occupied >= self.capacity:
            return ValidationError(_('Cannot join room %(room), is full.'),
                                   code='invalid',
                                   params={'room': self})

        # Remove user from previous rooms
        prev_room = user.room_of_user.filter(zosia=self.zosia).first()

        if prev_room:
            if prev_room.is_locked and prev_room.lock.owns(user):
                prev_room.lock.delete()

            prev_room.members.remove(user)

        if lock:
            if not self.lock or self.lock.is_expired:
                owner_lock = RoomLock.objects.make(user, expiration=expiration)
                self.lock = owner_lock

        self.save()

        return UserRoom.objects.create(room=self, user=user)

    @transaction.atomic
    def unlock(self, user):
        if self.is_locked and self.lock.owns(user):
            return self.lock.delete()

    def __str__(self):
        return 'Room ' + self.name


class UserRoom(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
