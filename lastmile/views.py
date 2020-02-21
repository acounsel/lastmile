from django.shortcuts import render
from django.views.generic import View, DetailView, ListView

from .models import Action, Actor, Commitment, Update


class CommitmentList(ListView):
    model = Commitment

class CommitmentDetail(DetailView):
    model = Commitment

class ActionList(ListView):
    model = Action

class ActionDetail(DetailView):
    model = Action

class ActorList(ListView):
    model = Actor

class ActorDetail(DetailView):
    model = Actor