from datetime import timedelta
import random
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from users.models import User


def random_string(length=10):
    return "".join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(length))


class RoomLockManager(models.Manager):
    # 3 hours
    TIMEOUT = timedelta(0, 3 * 3600)

    def make(self, user, expiration_date=None):
        if not expiration_date:
            expiration_date = timezone.now() + settings.LOCK_TIMEOUT

        return self.create(user=user, password=random_string(4), expiration_date=expiration_date)


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
        if "hidden" in params and params["hidden"]:
            return None

        params["hidden"] = False

        return self.filter(**params)


class Room(models.Model):
    objects = RoomManager()

    name = models.CharField(max_length=300)
    description = models.TextField(default="")
    hidden = models.BooleanField(default=False)
    beds_single = models.PositiveSmallIntegerField(default=0)
    beds_double = models.PositiveSmallIntegerField(default=0)
    available_beds_single = models.PositiveSmallIntegerField(default=0)
    available_beds_double = models.PositiveSmallIntegerField(default=0)

    lock = models.OneToOneField(RoomLock, on_delete=models.SET_NULL, blank=True, null=True)

    members = models.ManyToManyField(User, through="UserRoom", related_name="room_of_user")

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
    def members_count(self):
        return self.members.count()

    @property
    def is_locked(self):
        return self.lock and not self.lock.is_expired

    @property
    def is_full(self):
        return self.members_count >= self.capacity

    @property
    def members_to_string(self):
        return ", ".join(map(str, self.members.all()))

    def __str__(self):
        return "Room " + self.name

    @transaction.atomic
    def join(self, user, sender=None, password=None):
        if not sender:
            sender = user

        if self.hidden and not sender.is_staff:
            raise ValidationError(_("Cannot join %(room)s, room is unavailable."),
                                  code="invalid",
                                  params={"room": self})

        if self.is_locked and not self.lock.is_opened_by(password) \
                and not sender.is_staff:
            raise ValidationError(_("Cannot join %(room)s, room is locked."),
                                  code="invalid",
                                  params={"room": self})

        # Ensure room is not full
        if self.is_full:
            raise ValidationError(_("Cannot join %(room)s, room is full."),
                                  code="invalid",
                                  params={"room": self})

        # Remove user from previous room
        prev_room = user.room_of_user.all().first()

        if prev_room:
            prev_room.leave(user)

        self.members.add(user)
        self.save()

    @transaction.atomic
    def leave(self, user):
        try:
            self.unlock(user)
        except ValidationError:
            pass

        self.members.remove(user)
        self.save()

    @transaction.atomic
    def set_lock(self, owner, sender=None, expiration_date=None):
        if not sender:
            sender = owner

        if expiration_date and timezone.is_naive(expiration_date):
            expiration_date = timezone.make_aware(expiration_date)

        if not self.members.filter(pk__exact=owner.pk):
            raise ValidationError(_("Cannot lock %(room)s, user must first join the room."),
                                  code="invalid",
                                  params={"room": self})

        if self.hidden and not sender.is_staff:
            raise ValidationError(_("Cannot join %(room)s, room is unavailable."),
                                  code="invalid",
                                  params={"room": self})

        if self.is_locked and not sender.is_staff:
            raise ValidationError(_("Cannot lock %(room)s, room has already been locked."),
                                  code="invalid",
                                  params={"room": self})

        self.lock = RoomLock.objects.make(owner, expiration_date=expiration_date)
        self.lock.save()
        self.save()

    @transaction.atomic
    def unlock(self, sender):
        if self.is_locked:
            if not self.lock.is_owned_by(sender) and not sender.is_staff:
                raise ValidationError(_("Cannot unlock %(room)s, no permission to do this."),
                                      code="invalid",
                                      params={"room": self})

            lock = self.lock
            self.lock = None
            self.save()
            lock.delete()


class UserRoom(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(default=timezone.now)
