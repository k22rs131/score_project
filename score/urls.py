from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('score/', views.ListScoreView.as_view(), name='list-score'),
    path('score/<int:pk>/detail/', views.DetailScoreView.as_view(), name='detail-score'),
    path('score/<int:pk>/pdf/', views.ScorePdfView.as_view(), name='score-pdf'),
    path('score/create/', views.CreateScoreView.as_view(), name='create-score'),
    path('score/<int:pk>/delete/', views.DeleteScoreView.as_view(), name='delete-score'),
    path('score/<int:pk>/update', views.UpdateScoreView.as_view(), name='update-score'),
    path('score/<int:pk>/index', views.IndexScoreView.as_view(), name='index-score'),
]