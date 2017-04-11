from django.contrib.auth.models import User
from django.db import models


class OwnedModelMixin(models.Model):
    created_by = models.ForeignKey(User)

    class Meta:
        abstract = True


class TimestampedModelMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TimestampedOwnedModelMixin(OwnedModelMixin, TimestampedModelMixin):
    class Meta:
        abstract = True


class SoftDeletableModelMixin(models.Model):
    deleted = models.BooleanField(default=False, editable=False)

    class Meta:
        abstract = True
