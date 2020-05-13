from django.contrib import admin

from lastmile.models import Action, Actor, Agreement
from lastmile.models import Attachment, Commitment, Update
from lastmile.models import CommitmentCategory


admin.site.register(Actor)
admin.site.register(Action)
admin.site.register(Agreement)
admin.site.register(Attachment)
admin.site.register(Commitment)
admin.site.register(CommitmentCategory)
admin.site.register(Update)