import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify

class Agreement(models.Model):
    
    name = models.CharField(max_length=255)

class CommitmentCategory(models.Model):
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255, blank=True)
    description = models.TextField(blank=True)
    agreement = models.ForeignKey(Agreement,
        on_delete=models.SET_NULL,
        blank=True, null=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = self.create_unique_slug()
        super(CommitmentCategory, self).save(*args, **kwargs)

    def create_unique_slug(self):
        iterator = 1
        slug = slugify(self.name)
        while self.__class__.objects.exclude(id=self.id).filter(slug=slug):
            iterator += 1
            slug = slugify(self.name) + str(iterator)
        return slug
        
    def get_absolute_url(self):
        return reverse('commitment-category-detail',
            kwargs={'slug':self.slug})

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
    category = models.ForeignKey(CommitmentCategory,
        on_delete=models.SET_NULL,
        blank=True, null=True)
    agreement = models.ForeignKey(Agreement,
        on_delete=models.CASCADE,
        blank=True, null=True)
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES,
        default=PENDING)
    status_description = models.TextField(blank=True)
    expected_completion_date = models.DateField(
        blank=True, null=True)
    completion_date = models.DateField(
        blank=True, null=True)
    goal = models.CharField(max_length=255,
        blank=True)
    progress_toward_goal = models.CharField(max_length=255,
        blank=True)

    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('commitment-detail', kwargs={'pk':self.id})

    def save(self, *args, **kwargs):
        new = False
        if not self.id:
            new = True
        super(Commitment, self).save(*args, **kwargs)
        if new:
            update = Update.objects.create(
                description='Commitment Added',
                _type=Update.ADDITION,
                commitment=self,
            )

    def is_numeric(self):
        try:
            goal_num = int(self.goal)
            return True
        except Exception as e:
            return False
            
    def get_percent_progress(self):
        if self.is_numeric():
            if self.progress_toward_goal:
                try:
                    progress_num = int(
                        self.progress_toward_goal)
                    return progress_num / int(self.goal)
                except Exception as error:
                    return 0
        return None
    
    def get_status(self):
        date = self.expected_completion_date
        if date and self.status == self.ACTIVE:
            if date < datetime.date.today():
                return 'overdue'
            elif date + datetime.timedelta(days=7) < \
            datetime.date.today():
                return 'upcoming'
            else:
                return 'ongoing'
        return ''

    def get_status_color(self):
        if self.status == self.PENDING:
            return 'light'
        elif self.status == self.COMPLETE:
            return 'success'
        elif self.status == self.FAILED:
            return 'dark'
        else:
            status = self.get_status()
            if status == 'overdue':
                return 'danger'
            elif status == 'upcoming':
                return 'warning'
            else:
                return 'primary'
    
    def get_text_color(self):
        bg_color = self.get_status_color()
        if bg_color in ['light', 'warning']:
            return 'text-dark'
        else:
            return 'text-white'
    
    def is_delayed(self):
        if self.get_status() == 'overdue':
            return True

class Actor(models.Model):

    name = models.CharField(max_length=255)
    user = models.OneToOneField(User,
        on_delete=models.SET_NULL,
        blank=True, null=True)

    def __str__(self):
        if self.user:
            return '{} (User)'.format(self.name)
        return self.name

    def get_absolute_url(self):
        return reverse('actor-detail', kwargs={'pk':self.id})

    def get_completed_actions(self):
        return self.action_set.filter(status=Action.COMPLETE)

    def get_ongoing_actions(self):
        return self.action_set.filter(
            Q(status=Action.PENDING) | \
            Q(status=Action.ACTIVE))

    def get_overdue_actions(self):
        i = 0
        for action in self.action_set.filter(status=Action.ACTIVE):
            i += 1
        return i

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
        max_length=100, choices=STATUS_CHOICES,
        default=PENDING)
    status_description = models.TextField(blank=True)
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

    def get_absolute_url(self):
        return reverse('action-detail', kwargs={'pk':self.id})

    def save(self, *args, **kwargs):
        new = False
        if not self.id:
            new = True
        super(Action, self).save(*args, **kwargs)
        if new:
            update = Update.objects.create(
                description='Action Added',
                _type=Update.ADDITION,
                action=self,
                commitment=self.commitment,
            )

    def get_status(self):
        date = self.expected_completion_date
        if date and self.status == self.ACTIVE:
            if date < datetime.date.today():
                return 'overdue'
            elif date + datetime.timedelta(days=7) < \
            datetime.date.today():
                return 'upcoming'
            else:
                return 'ongoing'
        return ''

    def get_status_color(self):
        if self.status == self.PENDING:
            return 'light'
        elif self.status == self.COMPLETE:
            return 'success'
        elif self.status == self.FAILED:
            return 'dark'
        else:
            status = self.get_status()
            if status == 'overdue':
                return 'danger'
            elif status == 'upcoming':
                return 'warning'
            else:
                return 'primary'
    
    def get_text_color(self):
        bg_color = self.get_status_color()
        if bg_color in ['light', 'warning']:
            return 'text-dark'
        else:
            return 'text-white'
    
    def is_delayed(self):
        if self.get_status() == 'overdue':
            return True

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
    date_created = models.DateTimeField(auto_now_add=True)
    progress_toward_goal = models.CharField(max_length=255,
        blank=True)

    class Meta:
        ordering = ['-date_created']

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
            pass
        else:
            print('update_obj')
            for field in sender._meta.get_fields():
                Update.save_revision(
                    field, obj, instance, 'commitment')

    @receiver(pre_save, sender=Action)
    def save_action(sender, instance, **kwargs):
        try:
            obj = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
            # update = Update.save_addition(instance, 'action')
            # update.add_commitment()
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
        # setattr(update, model_name, instance)
        # update.save()
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
