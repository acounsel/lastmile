from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.Dashboard.as_view(), name='dashboard'),
    path('category/', include([
        path('', views.CommitmentCategoryList.as_view(), name='commitment-category-list'),
        path('add/', views.CommitmentCategoryCreate.as_view(), name='commitment-category-create'),
        path('<slug>/', include([
            path('', views.CommitmentCategoryDetail.as_view(), name='commitment-category-detail'),
            path('add-commitment/', views.CategoryCommitmentCreate.as_view(), name='category-commitment-create'),
            path('update', views.CommitmentCategoryUpdate.as_view(), name='commitment-category-update'),
        ])),
    ])),
    path('commitments/', include([
        path('', views.CommitmentList.as_view(), name='commitment-list'),
        path('add/',views.CommitmentCreate.as_view(), name='commitment-create'),
        path('<pk>/', include([
            path('', views.CommitmentDetail.as_view(), name='commitment-detail'),
            path('add-action/', views.CommitmentActionCreate.as_view(), name='commitment-action-create'),
            path('update/', views.CommitmentUpdate.as_view(), name='commitment-update'),
        ])),
        
    ])),
    path('actions/', include([
        path('',views.ActionList.as_view(), name='action-list'),
        path('add/',views.ActionCreate.as_view(), name='action-create'),
        path('<pk>/', include([
            path('',views.ActionDetail.as_view(), name='action-detail'),
            path('update/', views.ActionUpdate.as_view(), name='action-update'),
        ])),
        path('status/<status>/',views.ActionList.as_view(), name='action-list-by-status'),
    ])),
    path('actors/', include([
        path('',views.ActorList.as_view(), name='actor-list'),
        path('add/',views.ActorCreate.as_view(), name='actor-create'),
        path('<pk>/', include([
            path('',views.ActorDetail.as_view(), name='actor-detail'),
            path('update/', views.ActorUpdate.as_view(), name='actor-update'),
        ])),
    ])),
]
