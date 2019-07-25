import random
import string
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from users.models import User


def random_string(length=10):
    return ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(length))


class RoomLockManager(models.Manager):
    # 3 hours
    TIMEOUT = timedelta(0, 3 * 3600)

    def make(self, user, expiration_time=None):
        expiration_time = expiration_time or self.TIMEOUT

        return self.create(user=user, password=random_string(4),
                           expiration_date=timezone.now() + expiration_time)


class RoomLock(models.Model):
    objects = RoomLockManager()

    expiration_date = models.DateTimeField()
    password = models.CharField(max_length=4)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def is_expired(self):
        return self.expiration_date < timezone.now()

    def is_opened_by(self, password):
        return self.password == password

    def is_owned_by(self, user):
        return self.user == user


class RoomManager(models.Manager):
    def all_visible(self):
        return self.filter(hidden=False)

    def filter_visible(self, **params):
        if 'hidden' in params and params['hidden']:
            return None

        params["hidden"] = False

        return self.filter(**params)


class Room(models.Model):
    objects = RoomManager()

    name = models.CharField(max_length=300)
    description = models.TextField(default='')
    hidden = models.BooleanField(default=False)
    beds_single = models.IntegerField(default=0)
    beds_double = models.IntegerField(default=0)
    available_beds_single = models.IntegerField(default=0)
    available_beds_double = models.IntegerField(default=0)

    lock = models.ForeignKey(RoomLock, on_delete=models.SET_NULL, blank=True, null=True)

    members = models.ManyToManyField(User, through='UserRoom', related_name='room_of_user')

    @property
    def beds(self):
        return {"single": self.beds_single, "double": self.beds_double}

    @property
    def available_beds(self):
        return {"single": self.available_beds_single, "double": self.available_beds_double}

    @property
    def capacity(self):
        return self.available_beds_single + 2 * self.available_beds_double

    @property
    def is_locked(self):
        return self.lock and not self.lock.is_expired

    @property
    def is_occupied(self):
        return self.members.count()

    @property
    def is_full(self):
        return self.members.count() >= self.capacity

    @property
    def occupants(self):
        return ", ".join(map(str, self.members.all()))

    def __str__(self):
        return 'Room ' + self.name

    @transaction.atomic
    def join_and_lock(self, user, password='', expiration=None, lock=True):
        if self.is_locked and not self.lock.is_opened_by(password):
            return ValidationError(_('Cannot join room %(room), is locked.'),
                                   code='invalid',
                                   params={'room': self})

        # Ensure room is not full
        if self.is_occupied >= self.capacity:
            return ValidationError(_('Cannot join room %(room), is full.'),
                                   code='invalid',
                                   params={'room': self})

        # Remove user from previous rooms
        prev_room = user.room_of_user.all().first()

        if prev_room:
            if prev_room.is_locked and prev_room.lock.is_owned_by(user):
                prev_room.lock.delete()

            prev_room.members.remove(user)

        if lock:
            if not self.lock or self.lock.is_expired:
                self.lock = RoomLock.objects.make(user, expiration_time=expiration)

        self.save()

        return UserRoom.objects.create(room=self, user=user)

    @transaction.atomic
    def join(self, user, password=None):
        if self.is_locked and not self.lock.is_opened_by(password):
            return ValidationError(_('Cannot join room %(room), is locked.'),
                                   code='invalid',
                                   params={'room': self})

        # Ensure room is not full
        if self.is_full:
            return ValidationError(_('Cannot join room %(room), is full.'),
                                   code='invalid',
                                   params={'room': self})

        # Remove user from previous rooms
        prev_room = user.room_of_user.all().first()

        if prev_room:
            prev_room.leave(user)

        self.members.add(user)
        self.save()

    @transaction.atomic
    def leave(self, user):
        if self.is_locked and self.lock.is_owned_by(user):
            self.lock.delete()

        self.members.remove(user)
        self.save()

    @transaction.atomic
    def set_lock(self, user, expiration_time=None):
        self.lock = RoomLock.objects.make(user, expiration_time=expiration_time)
        self.save()

    @transaction.atomic
    def unlock(self, user):
        if self.is_locked and self.lock.is_owned_by(user):
            return self.lock.delete()


class UserRoom(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(default=timezone.now)
