from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.CommitmentList.as_view(), name='commitment-list'),
    path('commitments/', include([
        path('<pk>/',views.CommitmentDetail.as_view(), name='commitment-detail'),
    ])),
    path('actions/', include([
        path('',views.ActionList.as_view(), name='action-list'),
        path('<pk>/',views.ActionDetail.as_view(), name='action-detail'),
    ])),
    path('actors/', include([
        path('',views.ActorList.as_view(), name='actor-list'),
        path('<pk>/',views.ActorDetail.as_view(), name='actor-detail'),
    ])),
]
