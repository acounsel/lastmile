from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.urls import reverse, reverse_lazy
    
from .functions import get_export_response
from .models import Action, Actor, Agreement, Attachment
from .models import Commitment, CommitmentCategory, Update

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

class AgreementMixin(StaffMixin):
    login_url = '/login/'

    def get_agreement(self):
        if self.kwargs.get('agreement'):
            try:
                agreement = Agreement.objects.get(
                    slug=self.kwargs.get('agreement'))
                return agreement
            except Agreement.DoesNotExist:
                return None
        else:
            return Agreement.objects.filter(
                users=self.request.user)[0]

    # def test_func(self):
    #     user = self.request.user
    #     if user.is_authenticated and self.get_agreement():
    #         if user in self.get_agreement().users.all():
    #             return True
    #     else:
    #         return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agreement'] = self.get_agreement()
        return context

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

class BaseAgreementView(AgreementMixin, BaseView):
    pass

class DeleteView(StaffMixin, DeleteView):
    success_url = reverse_lazy('dashboard')
    template_name = 'lastmile/confirm_delete.html'
      
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Succesfully Deleted')
        return super().delete(request, *args, **kwargs)

class AgreementView(BaseAgreementView):
    model = Agreement
    fields = ['name', 'users']
    slug_url_kwarg = 'agreement'

    def get_queryset(self):
        queryset = super(
            AgreementView, self).get_queryset()
        return queryset.filter(users=self.request.user)

class AgreementDetail(AgreementView, DetailView):
    pass

class AgreementCreate(AgreementView, CreateView):
    pass

class AgreementUpdate(AgreementView, UpdateView):
    pass

class CommitmentCategoryView(BaseAgreementView):
    model = CommitmentCategory
    fields = ['name', 'description']

    def get_queryset(self):
        queryset = super(
            CommitmentCategoryView, self).get_queryset()
        agreements = self.request.user.agreement_set.all()
        return queryset.filter(agreement__in=agreements)

    def form_valid(self, form):
        form.instance.agreement = self.get_agreement()
        return super().form_valid(form)

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

class CommitmentView(BaseAgreementView):
    model = Commitment
    fields = ['name', 'description', 'category',
        'status', 'status_description',
        'expected_completion_date',
        'completion_date', 'goal',
        'progress_toward_goal']

    # def get_queryset(self):
    #     queryset = super(CommitmentView, self).get_queryset()
    #     agreements = self.request.user.agreement_set.all()
    #     return queryset.filter(agreement__in=agreements)

    # def get_queryset(self):
    #     queryset = super(CommitmentView, self).get_queryset()
    #     agreement = self.get_agreement()
    #     return queryset.filter(agreement=agreement)

    def form_valid(self, form):
        form.instance.agreement = self.get_agreement()
        return super().form_valid(form)

class CommitmentList(CommitmentView, ListView):
    pass

class CommitmentExport(ExportMixin, CommitmentList):
    pass
        
class CommitmentDetail(
    AttachmentMixin, CommitmentView, DetailView):
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

class ActionView(BaseAgreementView):
    model = Action
    fields = ['name', 'description', 'status',
        'status_description','commitment',
        'responsible_parties', 'expected_completion_date',
        'completion_date']
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        queryset = super(ActionView, self).get_queryset()
        agreements = self.request.user.agreement_set.all()
        return queryset.filter(
            commitment__agreement__in=agreements).distinct()

class ActionList(ActionView, ListView):
    
    def get_queryset(self):
        queryset = super(ActionList, self).get_queryset()
        if self.kwargs.get('status'):
            if self.kwargs.get('status') == 'overdue':
                agreement = self.get_agreement()
                actions = agreement.get_overdue_actions()
                action_ids = actions.values_list(
                    'id', flat=True)
                queryset = queryset.filter(id__in=action_ids)
            else:
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
    
    def get_success_url(self):
        if self.object.commitment:
            commitment = self.object.commitment
            return reverse_lazy('commitment-detail', kwargs={
                'pk': commitment.id,
                'agreement': commitment.agreement.slug,
            })
        else:
            return reverse_lazy('dashboard')

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
                'agreement':self.kwargs.get('agreement'),
                'pk':self.kwargs.get('pk')})

class ActorView(BaseAgreementView):
    model = Actor
    fields = ['name', 'user', 'agreement']
    success_url = reverse_lazy('dashboard')

    # def get_initial(self):
    #     agreement = self.get_agreement()
    #     return {'agreement': agreement}

    # def get_form(self, *args, **kwargs):
    #     form = super().get_form(*args, **kwargs)
    #     form.fields['agreement'].queryset = \
    #         Agreement.objects.filter(users=self.request.user)
    #     return form

class ActorList(ActorView, ListView):
    pass    
    # def get_queryset(self):
    #     queryset = super(ActorList, self).get_queryset()
    #     agreement = self.get_agreement()
    #     return queryset.filter(agreement=agreement)

class ActorDetail(ActorView, DetailView):
    pass

class ActorCreate(ActorView, CreateView):
    pass

class ActorUpdate(ActorView, UpdateView):
    pass

class ActorDelete(ActorView, DeleteView):
    pass

class AttachmentView(BaseAgreementView):
    model = Attachment
    fields = ['name', 'file', 'description', 'commitment', 
        'action']

    def get_queryset(self):
        queryset = super(
            AttachmentView, self).get_queryset()
        agreements = self.request.user.agreement_set.all()
        return queryset.filter(
            commitment__agreement__in=agreements)

    def get_success_url(self):
        attachment = self.get_object()
        if attachment.commitment:
            commitment = attachment.commitment
            return reverse('commitment-detail', kwargs={
                'pk':commitment.id,
                'agreement':commitment.agreement.slug
            })
        elif attachment.action:
            action = attachment.action
            return reverse('action-detail', kwargs={
                'pk':action.id,
                'attachment':action.commitment.agreement.slug
            })
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