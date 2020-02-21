from django.contrib import admin

from lastmile.models import Action, Actor, Commitment, Update

admin.site.register(Commitment)
admin.site.register(Actor)
admin.site.register(Action)
admin.site.register(Update)