import csv
import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from django_lastmile import storage_backends

class Agreement(models.Model):
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255, blank=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = self.create_unique_slug()
        super(Agreement, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('agreement-detail', kwargs={
            'agreement':self.slug})

    def get_action_items(self):
        return Action.objects.filter(
            commitment__agreement=self).distinct()

    def get_complete_actions(self):
        action_items = self.get_action_items()
        return action_items.filter(status=Action.COMPLETE)

    def get_active_actions(self):
        action_items = self.get_action_items()
        return action_items.filter(status=Action.ACTIVE)

    def get_pending_actions(self):
        action_items = self.get_action_items()
        return action_items.filter(status=Action.PENDING)

    def get_overdue_actions(self):
        overdue = []
        action_items = self.get_action_items()
        for item in action_items:
            if item.get_status() == 'overdue':
                overdue.append(item.id)
        actions = Action.objects.filter(id__in=overdue)
        return actions

    def create_unique_slug(self):
        iterator = 1
        slug = slugify(self.name)
        while self.__class__.objects.exclude(
            id=self.id).filter(slug=slug):
            iterator += 1
            slug = slugify(self.name) + str(iterator)
        return slug

    def get_status_dict(self, model, queryset):
        status_dict = {}
        for status in model.STATUS_CHOICES:
            status_dict[status[0]] = (
                status[1], 
                queryset.filter(status=status[0])
            )
            if status[0] == 'active':
                status_dict = self.separate_overdue_items(
                    status_dict)
        return status_dict

    def get_commitment_dict(self):
        return self.get_status_dict(
            model=Commitment, 
            queryset=self.commitment_set.all()
        )

    def get_action_dict(self):
        return self.get_status_dict(
            model=Action, 
            queryset=self.get_action_items()
        )

    def get_overdue_items(self, queryset):
        overdue = []
        for item in queryset:
            if item.get_status() == 'overdue':
                overdue.append(item.id)
        return queryset.filter(id__in=overdue)

    def get_overdue_commitments(self):
        overdue = []
        for item in self.commitment_set.all():
            if item.get_status() == 'overdue':
                overdue.append(item.id)
        return Commitment.objects.filter(id__in=overdue)

    def separate_overdue_items(self, item_dict):
        queryset = item_dict['active'][1]
        overdue_items = self.get_overdue_items(queryset)
        item_dict['overdue'] = ('Overdue', overdue_items)
        item_dict['active'] = (
            'Active (not overdue)',
            queryset.exclude(
                id__in=overdue_items.values_list(
                    'id', flat=True))
        )
        return item_dict

class Overview(models.Model):

    name = models.CharField(max_length=255)
    agreement = models.OneToOneField(Agreement, 
        on_delete=models.SET_NULL, blank=True, null=True)
    subtitle = models.CharField(max_length=255, 
        blank=True)
    hero_video = models.CharField(max_length=255, 
        blank=True)
    hero_image = models.ImageField(
        storage=storage_backends.PrivateMediaStorage(), 
        upload_to='images/', blank=True, null=True)
    story_image = models.ImageField(
        storage=storage_backends.PrivateMediaStorage(), 
        upload_to='images/', blank=True, null=True)
    story_part1 = models.TextField(blank=True)
    story_part2 = models.TextField(blank=True)
    story_part3 = models.TextField(blank=True)
    achievements_text = models.TextField(blank=True)
    challenges_text = models.TextField(blank=True)
    commitment_chart_text = models.TextField(blank=True)
    commitments_image = models.ImageField(
        storage=storage_backends.PrivateMediaStorage(), 
        upload_to='images/', blank=True, null=True)
    about_us = models.TextField(blank=True)
    methodology = models.TextField(blank=True)
    report_name = models.CharField(max_length=255, 
        blank=True)
    report = models.URLField(max_length=255, blank=True)
    case_page = models.URLField(max_length=255, blank=True)
    highlight_color = models.CharField(max_length=7, 
        blank=True, null=True)
    special_text_color = models.CharField(max_length=7, 
        blank=True, null=True)
    bg_color = models.CharField(max_length=7, 
        blank=True, null=True)
    bg_color_2 = models.CharField(max_length=7, 
        blank=True, null=True)
    bg_color_3 = models.CharField(max_length=7, 
        blank=True, null=True)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('overview-detail', kwargs={
            'agreement':self.agreement.slug, 'pk':self.id})

class CommitmentCategory(models.Model):
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255, blank=True)
    description = models.TextField(blank=True)
    agreement = models.ForeignKey(Agreement,
        on_delete=models.SET_NULL,
        blank=True, null=True)
    order_num = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ('order_num',)
        verbose_name_plural = 'commitment categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = self.create_unique_slug()
        super(CommitmentCategory, self).save(*args, **kwargs)

    def create_unique_slug(self):
        iterator = 1
        slug = slugify(self.name)
        while self.__class__.objects.exclude(
            id=self.id).filter(slug=slug):
            iterator += 1
            slug = slugify(self.name) + str(iterator)
        return slug
        
    def get_absolute_url(self):
        return reverse('commitment-category-detail',
            kwargs={
                'slug':self.slug,
                'agreement':self.agreement.slug
            })

    def get_delete_url(self):
        return reverse('commitment-category-delete',
            kwargs={
                'slug':self.slug,
                'agreement':self.agreement.slug
            })

class Commitment(models.Model):
    PENDING = 'pending'
    ACTIVE = 'active'
    COMPLETE = 'complete'
    FAILED = 'failed'
    UNKNOWN = 'unknown'
    STATUS_CHOICES = (
        (PENDING, 'Not Started'),
        (ACTIVE, 'Active'),
        (COMPLETE, 'Complete'),
        (FAILED, 'Failed'),
        (UNKNOWN, 'Unknown'),
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
    order_num = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ('category', 'order_num')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('commitment-detail', kwargs={
            'pk':self.id, 
            'agreement':self.agreement.slug})

    def get_delete_url(self):
        return reverse('commitment-delete', kwargs={
            'pk':self.id,
            'agreement':self.agreement.slug})

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

    def get_actions(self):
        return self.action_set.order_by('status')

    def get_active_actions(self):
        return self.action_set.filter(status=Action.ACTIVE)

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
        if bg_color in ['light', 'warning', 'primary']:
            return 'text-dark'
        else:
            return 'text-white'
    
    def is_delayed(self):
        if self.get_status() == 'overdue':
            return True

class Actor(models.Model):

    name = models.CharField(max_length=255)
    agreement = models.ManyToManyField(Agreement, 
        blank=True)
    user = models.OneToOneField(User,
        on_delete=models.SET_NULL,
        blank=True, null=True)

    def __str__(self):
        if self.user:
            return '{} (User)'.format(self.name)
        return self.name

    def get_absolute_url(self):
        return reverse('actor-detail', kwargs={
            'pk':self.id,
            'agreement':self.agreement.first().slug})

    def get_delete_url(self):
        return reverse('actor-delete', kwargs={
            'pk':self.id,
            'agreement':self.agreement.first().slug})

    def get_completed_actions(self):
        return self.action_set.filter(status=Action.COMPLETE)

    def get_ongoing_actions(self):
        return self.action_set.filter(
            Q(status=Action.PENDING) | \
            Q(status=Action.ACTIVE))

    def get_overdue_actions(self):
        i = 0
        for action in self.action_set.filter(
            status=Action.ACTIVE):
            if action.get_status() == 'overdue':
                i += 1
        return i

class Action(models.Model):
    PENDING = 'pending'
    ACTIVE = 'active'
    COMPLETE = 'complete'
    FAILED = 'failed'
    UNKNOWN = 'unknown'
    STATUS_CHOICES = (
        (PENDING, 'Not Started'),
        (ACTIVE, 'Active'),
        (COMPLETE, 'Complete'),
        (FAILED, 'Failed'),
        (UNKNOWN, 'Unknown'),
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
        blank=True, null=True, related_name='deprecated')
    responsible_parties = models.ManyToManyField(Actor,
        blank=True)
    expected_completion_date = models.DateField(
        blank=True, null=True)
    completion_date = models.DateField(
        blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('action-detail', kwargs={
            'pk':self.id,
            'agreement':self.commitment.agreement.slug})

    def get_delete_url(self):
        return reverse('action-delete', kwargs={
            'pk':self.id,
            'agreement':self.commitment.agreement.slug})

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
        if bg_color in ['light', 'warning', 'primary']:
            return 'text-dark'
        else:
            return 'text-white'
    
    def is_delayed(self):
        if self.get_status() == 'overdue':
            return True

class Attachment(models.Model):

    name = models.CharField(max_length=255)
    file = models.FileField(
        storage=storage_backends.PrivateMediaStorage(),
        upload_to='files/', blank=True, null=True)
    description = models.TextField(blank=True)
    commitment = models.ForeignKey(Commitment, 
        models.SET_NULL, blank=True, null=True)
    action = models.ForeignKey(Action, 
        on_delete=models.SET_NULL, blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, 
        on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('attachment-detail', kwargs={
            'pk':self.id,
            'agreement':self.commitment.agreement.slug})

    def get_delete_url(self):
        return reverse('attachment-delete', kwargs={
            'pk':self.id,
            'agreement':self.commitment.agreement.slug})

    def save(self, *args, **kwargs):
        new = False
        if not self.id:
            new = True
        if self.action:
            self.commitment = self.action.commitment
        super(Attachment, self).save(*args, **kwargs)
        if new:
            update = Update.objects.create(
                description='Attachment Added',
                _type=Update.OTHER,
                commitment=self.commitment,
                action=self.action,
            )

class UpdateManager(models.Manager):

    def add_delay(self, action, date):
        delay = date - action.expected_completion_date
        update = Update.objects.create(
            description='{0} Days Past Deadline - {1}'.format(
                delay.days,
                action.expected_completion_date
            ),
            _type=Update.DELAY,
            commitment=action.commitment,
            action=action,
            actor=action.responsible_party,
        )
        return update

class Update(models.Model):
    objects = UpdateManager()
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
            for field in sender._meta.get_fields():
                Update.save_revision(
                    field, obj, instance, 'commitment')

    @receiver(pre_save, sender=Action)
    def save_action(sender, instance, **kwargs):
        try:
            obj = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
        else:
            for field in sender._meta.get_fields():
                update = Update.save_revision(
                    field, obj, instance, 'action')
                if update:
                    update.add_commitment()

    @receiver(pre_save, sender=Attachment)
    def save_attachment(sender, instance, **kwargs):
        try:
            obj = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
        else:
            for field in ('file', 'description', 
                'commitment', 'action'):
                update = Update.save_attachment_revision(
                    field, obj, instance)

    def save_attachment_revision(field, obj, instance):
        try:
            old = getattr(obj, field)
            new = getattr(instance, field)
            if old != new:
                update = Update.objects.create(
                    _type=Update.OTHER,
                    description=Update.get_description_string(
                    instance, old, new, field)
                )
                for field in ('action', 'commitment'):
                    setattr(update, field, 
                        getattr(instance, field)
                    )
                update.save()
                return update
        except Exception as error:
            print(error)
            pass

    def get_description_string(instance, old, new, field):
        if old in (None, ''):
            if field in ('commitment', 'action'):
                description = '{0} Added by {1}'.format(
                    instance.name, instance.uploaded_by)
            else:
                description = '{0} {1} Added by {2}'.format(
                    instance.name, 
                    field, 
                    instance.uploaded_by
                )
        else:
            description = '{0} {1} changed \
                from {2} to {3}'.format(
                    instance.name, field, old, new)
        return 'Attachment: {}'.format(description)

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
                    description='{0} changed from {1} to {2}'\
                    .format(field.name.title(), old, new),
                    _type=Update.REVISION,
                )
                setattr(update, model_name, instance)
                update.save()
                return update
        except Exception as error:
            print(error)
            pass

class OverviewModel(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(
        storage=storage_backends.PrivateMediaStorage(), 
        upload_to='images/', blank=True, null=True)
    commitments = models.ManyToManyField(Commitment, 
        blank=True)
    overview = models.ForeignKey(Overview, 
        on_delete=models.SET_NULL, blank=True, null=True)
    order_id = models.PositiveSmallIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ('order_id',)

    def __str__(self):
        return self.name

class Document(models.Model):

    name = models.CharField(max_length=255)
    document = models.FileField(
        storage=storage_backends.PrivateMediaStorage(), 
        upload_to='docs/', blank=True, null=True)
    description = models.TextField(blank=True)
    date = models.DateField(blank=True, null=True)
    overview = models.ForeignKey(Overview, 
        on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('date',)

class Achievement(OverviewModel):

    def get_update_url(self):
        return reverse('achievement-update', kwargs={
            'agreement':self.overview.agreement.slug,
            'pk': self.overview.id,
            'om_pk': self.id
        })

class Challenge(OverviewModel):

    def get_update_url(self):
        return reverse('challenge-update', kwargs={
            'agreement':self.overview.agreement.id,
            'pk': self.overview.id,
            'om_pk': self.id
        })

class Recommendation(OverviewModel):

    def get_update_url(self):
        return reverse('recommendation-update', kwargs={
            'agreement':self.overview.agreement.id,
            'pk': self.overview.id,
            'om_pk': self.id
        })

