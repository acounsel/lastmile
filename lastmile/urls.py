from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.Dashboard.as_view(), name='dashboard'),
    path('<agreement>/', include([
        path('', views.AgreementDetail.as_view(), name='agreement-detail'),
        path('category/', include([
            path('', views.CommitmentCategoryList.as_view(), name='commitment-category-list'),
            path('add/', views.CommitmentCategoryCreate.as_view(), name='commitment-category-create'),
            path('<slug>/', include([
                path('', views.CommitmentCategoryDetail.as_view(), name='commitment-category-detail'),
                path('add-commitment/', views.CategoryCommitmentCreate.as_view(), name='category-commitment-create'),
                path('update/', views.CommitmentCategoryUpdate.as_view(), name='commitment-category-update'),
                path('delete/', views.CommitmentCategoryDelete.as_view(), name='commitment-category-delete'),
            ])),
        ])),
        path('commitments/', include([
            path('', views.CommitmentList.as_view(), name='commitment-list'),
            path('add/',views.CommitmentCreate.as_view(), name='commitment-create'),
            path('export/', views.CommitmentExport.as_view(), name='commitment-export'),
            path('<pk>/', include([
                path('', views.CommitmentDetail.as_view(), name='commitment-detail'),
                path('add-action/', views.CommitmentActionCreate.as_view(), name='commitment-action-create'),
                path('update/', views.CommitmentUpdate.as_view(), name='commitment-update'),
                path('delete/', views.CommitmentDelete.as_view(), name='commitment-delete'),
            ])),
        ])),
        path('actions/', include([
            path('',views.ActionList.as_view(), name='action-list'),
            path('add/',views.ActionCreate.as_view(), name='action-create'),
            path('export/',views.ActionExport.as_view(), name='action-export'),
            path('<pk>/', include([
                path('',views.ActionDetail.as_view(), name='action-detail'),
                path('update/', views.ActionUpdate.as_view(), name='action-update'),
                path('delete/', views.ActionDelete.as_view(), name='action-delete'),
            ])),
            path('status/<status>/',views.ActionList.as_view(), name='action-list-by-status'),
        ])),
        path('actors/', include([
            path('',views.ActorList.as_view(), name='actor-list'),
            path('add/',views.ActorCreate.as_view(), name='actor-create'),
            path('<pk>/', include([
                path('',views.ActorDetail.as_view(), name='actor-detail'),
                path('update/', views.ActorUpdate.as_view(), name='actor-update'),
                path('delete/', views.ActorDelete.as_view(), name='actor-delete'),
            ])),
        ])),
        path('attachments/', include([
            path('',views.AttachmentList.as_view(), name='attachment-list'),
            path('add/', views.AttachmentCreate.as_view(), name='attachment-create'),
            path('<pk>/', include([
                path('', views.AttachmentDetail.as_view(), name='attachment-detail'),
                path('update/', views.AttachmentUpdate.as_view(), name='attachment-update'),
                path('delete/', views.AttachmentDelete.as_view(), name='attachment-delete'),
            ])),
        ])),
        path('overview/', include([
            path('add/', views.OverviewCreate.as_view(), name='overview-create'),
            path('<pk>/', include([
                path('', views.OverviewDetail.as_view(), name='overview-detail'),
                path('challenges/', include([
                    path('', views.ChallengeList.as_view(), name='challenge-list'),
                    path('add/', views.ChallengeCreate.as_view(), name='challenge-create'),
                    path('<om_pk>/', views.ChallengeUpdate.as_view(), name='challenge-update'),
                ])),
                path('achievements/', include([
                    path('', views.AchievementList.as_view(), name='achievement-list'),
                    path('add/', views.AchievementCreate.as_view(), name='achievement-create'),
                    path('<om_pk>/', views.AchievementUpdate.as_view(), name='achievement-update'),
                ])),
                path('recommendations/', include([
                    path('', views.RecommendationList.as_view(), name='recommendation-list'),
                    path('add/', views.RecommendationCreate.as_view(), name='recommendation-create'),
                    path('<om_pk>/', views.RecommendationUpdate.as_view(), name='recommendation-update'),
                ])),
                path('update/', views.OverviewUpdate.as_view(), name='overview-update'),
                path('delete/', views.OverviewDelete.as_view(), name='overview-delete'),
                path('methodology/', views.Methodology.as_view(), name='methodology'),
            ])),
            
        ])),
    ])),
]
