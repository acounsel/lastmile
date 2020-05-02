from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.urls import reverse, reverse_lazy
    
from .functions import get_export_response
from .models import Action, Actor, Commitment
from .models import CommitmentCategory, Update
from .models import Attachment

class ExportMixin():

    def get(self, request, **kwargs):
        resp = super().get(request, **kwargs)
        response = get_export_response(
            self.model, 
            self.get_queryset())
        return response

class StaffMixin(UserPassesTestMixin):
    login_url = '/login/'

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.is_staff
        else:
            return False

class AttachmentMixin():

    def post(self, request, **kwargs):
        user = request.user
        attachment = Attachment.objects.create(
            name=request.POST.get('name'), 
            file=request.FILES.get('file'),
            description=request.POST.get('description'),
            uploaded_by=user,
        )
        field = self.model._meta.verbose_name
        value = self.get_object()
        setattr(attachment, field, value)
        attachment.save()
        messages.success(request, 'Attachment Added')
        return redirect(value.get_absolute_url())

class BaseView(LoginRequiredMixin, View):
    login_url = '/login/'

class CommitmentCategoryView(BaseView):
    model = CommitmentCategory
    fields = ['name', 'description']

class DeleteView(StaffMixin, DeleteView):
    success_url = reverse_lazy('dashboard')
    template_name = 'lastmile/confirm_delete.html'
      
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Succesfully Deleted')
        return super().delete(request, *args, **kwargs)

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

class CommitmentCategoryDelete(
    CommitmentCategoryView, DeleteView):
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
        
class CommitmentDetail(AttachmentMixin, CommitmentView, DetailView):
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

class CommitmentDelete(CommitmentView, DeleteView):
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

class ActionDetail(ActionView, DetailView, AttachmentMixin):
    pass

class ActionCreate(ActionView, CreateView):
    pass

class ActionUpdate(ActionView, UpdateView):
    pass

class ActionDelete(ActionView, DeleteView):
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

class ActorDelete(ActorView, DeleteView):
    pass

class AttachmentView(BaseView):
    model = Attachment
    fields = ['name', 'file', 'description', 'commitment', 
        'action']

    def get_success_url(self):
        attachment = self.get_object()
        if attachment.commitment:
            return reverse('commitment-detail',
                kwargs={'pk':attachment.commitment.id})
        elif attachment.action:
            return reverse('action-detail', 
                kwargs={'pk':attachment.action.id})
        else:
            return reverse('dashboard')

class AttachmentList(AttachmentView, ListView):
    pass

class AttachmentCreate(AttachmentView, CreateView):
    
    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)

class AttachmentDetail(AttachmentView, DetailView):
    pass

class AttachmentUpdate(AttachmentView, UpdateView):
    pass

class AttachmentDelete(AttachmentView, DeleteView):
    pass