import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse

class Commitment(models.Model):
    PENDING = 'pending'
    ACTIVE = 'active'
    COMPLETE = 'complete'
    FAILED = 'failed'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (COMPLETE, 'Complete'),
        (FAILED, 'Failed'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES)
    expected_completion_date = models.DateField(
        blank=True, null=True)
    completion_date = models.DateField(
        blank=True, null=True)
    
    target_number = models.IntegerField(
        blank=True, null=True)
    achieved_number = models.IntegerField(
        blank=True, null=True)

    def __str__(self):
        return '{0}: {1}'.format(
            self.name, self.get_status_display())

    def get_absolute_url(self):
        return reverse('commitment-detail', kwargs={'pk':self.id})

class Actor(models.Model):

    name = models.CharField(max_length=255)
    user = models.OneToOneField(User, 
        on_delete=models.SET_NULL,
        blank=True, null=True)

    def __str__(self):
        if self.user:
            return '{} (User)'.format(self.name)
        return self.name

    def get_completed_actions(self):
        return self.action_set.filter(status=Action.COMPLETE)

    def get_ongoing_actions(self):
        return self.action_set.filter(
            Q(status=Action.PENDING) | \
            Q(status=Action.ACTIVE))

    def get_overdue_actions(self):
        return self.action_set.filter(status=Action.COMPLETE)

class Action(models.Model):
    PENDING = 'pending'
    ACTIVE = 'active'
    COMPLETE = 'complete'
    FAILED = 'failed'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (COMPLETE, 'Complete'),
        (FAILED, 'Failed'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES)
    commitment = models.ForeignKey(Commitment, 
        on_delete=models.CASCADE,
        blank=True, null=True)
    responsible_party = models.ForeignKey(Actor, 
        on_delete=models.SET_NULL,
        blank=True, null=True)
    expected_completion_date = models.DateField(
        blank=True, null=True)
    completion_date = models.DateField(
        blank=True, null=True)

    def __str__(self):
        return self.name

    def get_status(self):
        date = self.expected_completion_date
        if date and self.status == self.ACTIVE:
            if date < datetime.date.today():
                return 'overdue'
            elif date + datetime.delta(days=7) < \
            datetime.date.today():
                return 'upcoming'
        return 'ongoing'

    def get_status_color(self):
        if self.status == self.PENDING:
            return 'light'
        elif self.status == self.COMPLETE:
            return 'success text-white'
        elif self.status == self.FAILED:
            return 'dark text-white'
        else:
            status = self.get_status()
            if status == 'overdue':
                return 'danger text-white'
            elif status == 'upcoming':
                return 'warning'
            else:
                return 'primary text-white'

class Update(models.Model):
    # Delays refer to active actions that have passed their 
    #  expected completion date
    DELAY = 'delay'
    # Revisions are updates/edits to existing model instances
    REVISION = 'revision'
    # Additions are creations of new modal instances
    ADDITION = 'addition'
    # Status Change refers to an update 
    #  on action/commitment status
    STATUS_CHANGE = 'status'
    # Catch-all for any remaining updates
    OTHER = 'other'
    TYPE_CHOICES = (
        (DELAY, 'Delay'),
        (REVISION, 'Revision'),
        (ADDITION, 'Addition'),
        (STATUS_CHANGE, 'Status Change'),
        (OTHER, 'Other'),
    )

    description = models.TextField(blank=True)
    _type = models.CharField(max_length=100, 
        choices=TYPE_CHOICES, default=OTHER)
    commitment = models.ForeignKey(Commitment, 
        on_delete=models.SET_NULL,
        blank=True, null=True)
    action = models.ForeignKey(Action, 
        on_delete=models.SET_NULL,
        blank=True, null=True)
    actor = models.ForeignKey(Actor, 
        on_delete=models.SET_NULL,
        blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    achieved_number = models.IntegerField(
        blank=True, null=True)

    def __str__(self):
        if self.action:
            return '{0} - {1} - {2} - {3}'.format(
                self.get__type_display(), 
                self.action, 
                self.commitment,
                self.date_created
            )
        else:
            return '{0} - {1} - {2}'.format(
                self.get__type_display(), 
                self.commitment,
                self.date_created
            )

    def add_commitment(self):
        if self.action:
            self.commitment = self.action.commitment
            self.save()
        return self

    @receiver(pre_save, sender=Commitment)
    def save_commitment(sender, instance, **kwargs):
        try:
            obj = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            Update.save_addition(instance, 'commitment')
        else:
            for field in sender._meta.get_fields():
                Update.save_revision(
                    field, obj, instance, 'commitment')

    @receiver(pre_save, sender=Action)
    def save_commitment(sender, instance, **kwargs):
        try:
            obj = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            update = Update.save_addition(instance, 'action')
            update.add_commitment()
        else:
            for field in sender._meta.get_fields():
                update = Update.save_revision(
                    field, obj, instance, 'action')
                if update:
                    update.add_commitment()

    def save_addition(instance, model_name):
        update = Update.objects.create(
            description='{0} added'.format(
                model_name.title()),
            _type=Update.ADDITION,
        )
        setattr(update, model_name, instance)
        update.save()
        return update

    def save_revision(field, obj, instance, model_name):
        try:
            old = getattr(obj, field.name)
            new = getattr(instance, field.name)
            if old != new:
                update = Update.objects.create(
                    description='{0} changed from {1} to {2}' \
                    .format(field.name.title(), old, new),
                    _type=Update.REVISION,
                )
                setattr(update, model_name, instance)
                update.save()
                return update
        except Exception as error:
            print(error)  
            pass
