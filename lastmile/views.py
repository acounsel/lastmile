from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse

from .models import Action, Actor, Commitment, Update

class CommitmentView(LoginRequiredMixin, View):
    login_url = '/login/'
    model = Commitment
    fields = ['name', 'description', 'status',
        'status_description', 'expected_completion_date',
        'completion_date', 'target_number',
        'achieved_number']

class CommitmentList(CommitmentView, ListView):
    pass

class CommitmentDetail(CommitmentView, DetailView):
    pass

class CommitmentCreate(CommitmentView, CreateView):
    pass

class CommitmentUpdate(CommitmentView, UpdateView):
    pass

class Dashboard(CommitmentList):
    template_name = 'lastmile/dashboard.html'

class ActionView(LoginRequiredMixin, View):
    login_url = '/login/'
    model = Action
    fields = ['name', 'description', 'status',
        'status_description','commitment',
        'responsible_party', 'expected_completion_date',
        'completion_date']

class ActionList(ActionView, ListView):
    
    def get_queryset(self):
        queryset = super(ActionList, self).get_queryset()
        if self.kwargs.get('status'):
            queryset = queryset.filter(
                status=self.kwargs.get('status'))
        return queryset

class ActionDetail(ActionView, DetailView):
    pass

class ActionCreate(ActionView, CreateView):
    pass

class ActionUpdate(ActionView, UpdateView):
    pass

class CommitmentActionCreate(ActionCreate):
    
    def get_initial(self):
        initial = super(CommitmentActionCreate, self).get_initial()
        commitment = Commitment.objects.get(id=self.kwargs.get('pk'))
        initial['commitment'] = commitment
        return initial.copy()
    
    def get_success_url(self):
        return reverse('commitment-detail', kwargs={
                'pk':self.kwargs.get('pk')})

class ActorView(LoginRequiredMixin, View):
    login_url = '/login/'
    model = Actor
    fields = ['name', 'user']

class ActorList(ActorView, ListView):
    pass

class ActorDetail(ActorView, DetailView):
    pass

class ActorCreate(ActorView, CreateView):
    pass

class ActorUpdate(ActorView, UpdateView):
    pass