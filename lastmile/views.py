from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse

from .functions import get_export_response
from .models import Action, Actor, Commitment
from .models import CommitmentCategory, Update

class ExportMixin():

    def get(self, request, **kwargs):
        resp = super().get(request, **kwargs)
        response = get_export_response(
            self.model, 
            self.get_queryset())
        return response

class BaseView(LoginRequiredMixin, View):
    login_url = '/login/'

class CommitmentCategoryView(BaseView):
    model = CommitmentCategory
    fields = ['name', 'description']
    
class CommitmentCategoryList(
    CommitmentCategoryView, ListView):
    pass

class CommitmentCategoryDetail(
    CommitmentCategoryView, DetailView):
    pass

class CommitmentCategoryCreate(
    CommitmentCategoryView, CreateView):
    pass

class CommitmentCategoryUpdate(
    CommitmentCategoryView, UpdateView):
    pass

class CommitmentView(BaseView):
    model = Commitment
    fields = ['name', 'description', 'category',
        'status', 'status_description',
        'expected_completion_date',
        'completion_date', 'goal',
        'progress_toward_goal']

class CommitmentList(CommitmentView, ListView):
    pass

class CommitmentExport(ExportMixin, CommitmentList):
    pass
        
class CommitmentDetail(CommitmentView, DetailView):
    pass

class CommitmentCreate(CommitmentView, CreateView):
    pass

class CategoryCommitmentCreate(
    CommitmentCreate):
    
    def get_initial(self):
        initial = super(
            CategoryCommitmentCreate, self).get_initial()
        category = CommitmentCategory.objects.get(
            slug=self.kwargs.get('slug'))
        initial['category'] = category
        return initial.copy()
    
    def get_success_url(self):
        return reverse('commitment-category-detail',
            kwargs={ 'slug':self.kwargs.get('slug')})

class CommitmentUpdate(CommitmentView, UpdateView):
    pass

class Dashboard(CommitmentList):
    template_name = 'lastmile/dashboard.html'

class ActionView(BaseView):
    model = Action
    fields = ['name', 'description', 'status',
        'status_description','commitment',
        'responsible_parties', 'expected_completion_date',
        'completion_date']

class ActionList(ActionView, ListView):
    
    def get_queryset(self):
        queryset = super(ActionList, self).get_queryset()
        if self.kwargs.get('status'):
            queryset = queryset.filter(
                status=self.kwargs.get('status'))
        return queryset

class ActionExport(ExportMixin, ActionList):
    pass

class ActionDetail(ActionView, DetailView):
    pass

class ActionCreate(ActionView, CreateView):
    pass

class ActionUpdate(ActionView, UpdateView):
    pass

class CommitmentActionCreate(ActionCreate):
    
    def get_initial(self):
        initial = super(CommitmentActionCreate, self) \
            .get_initial()
        commitment = Commitment.objects.get(
            id=self.kwargs.get('pk'))
        initial['commitment'] = commitment
        return initial.copy()
    
    def get_success_url(self):
        return reverse('commitment-detail', kwargs={
                'pk':self.kwargs.get('pk')})

class ActorView(BaseView):
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