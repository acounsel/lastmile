from django.contrib import admin

from lastmile.models import Action, Actor, Commitment, Update
from lastmile.models import CommitmentCategory


admin.site.register(Actor)
admin.site.register(Action)
admin.site.register(Commitment)
admin.site.register(CommitmentCategory)
admin.site.register(Update)