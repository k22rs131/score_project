from django.urls import path
from . import views

urlpatterns = [
    path('score/', views.ListScoreView.as_view(), name='list-score'),
    path('score/search/', views.SearchScoreView.as_view(), name='search-score'),
    path('score/<int:pk>/detail/', views.DetailScoreView.as_view(), name='detail-score'),
    path('score/<int:pk>/pdf/', views.ScorePdfView.as_view(), name='score-pdf'),
    path('score/create/', views.CreateScoreView.as_view(), name='create-score'),
    path('score/<int:pk>/delete/', views.DeleteScoreView.as_view(), name='delete-score'),
    path('score/<int:pk>/update/', views.UpdateScoreView.as_view(), name='update-score'),
]