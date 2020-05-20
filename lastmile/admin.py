from django.contrib import admin

from lastmile.models import Action, Actor, Agreement
from lastmile.models import Attachment, Commitment, Update
from lastmile.models import CommitmentCategory




@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_items = (
        'name',
    )
    list_display = list_items
    list_display_links = list_items
    list_filter = ('users',)

@admin.register(CommitmentCategory)
class CommitmentCategoryAdmin(admin.ModelAdmin):
    list_items = (
        'name',
        'agreement',
    )
    list_display = list_items
    list_display_links = list_items
    list_filter = ('agreement',)

@admin.register(Commitment)
class CommitmentAdmin(admin.ModelAdmin):
    list_items = (
        'name',
        'category',
        'status',
    )
    list_display = list_items
    list_display_links = list_items
    list_filter = ('category','agreement')

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_items = (
        'name',
        'status',
        'commitment',
        'responsible_party',
    )
    list_display = list_items
    list_display_links = list_items
    list_filter = ('status', 'commitment', 'responsible_party')

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_items = (
        'name',
        'user',
    )
    list_display = list_items
    list_display_links = list_items
    list_filter = ('agreement',)

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_items = (
        'name',
        'file',
        'commitment',
        'action',
    )
    list_display = list_items
    list_display_links = list_items
    list_filter = ('commitment','action')

@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = (
        '_type',
        'commitment',
        'action',
        'actor',
        'date_created',
    )
    list_display_links = (
        '_type',
        'commitment',
        'action',
        'actor',
        'date_created',
    )
    list_select_related = ('commitment', 'actor', 'action')
    list_filter = ('commitment', 'actor', 'action')

