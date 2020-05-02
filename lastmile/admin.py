from django.contrib import admin

from lastmile.models import Action, Actor, Commitment, Update
from lastmile.models import CommitmentCategory, Attachment


admin.site.register(Actor)
admin.site.register(Action)
admin.site.register(Commitment)
admin.site.register(CommitmentCategory)
admin.site.register(Update)
admin.site.register(Attachment)