from django.urls import path

from test_task import views


app_name = 'test_task'
urlpatterns = [
    path('handbooks/', views.HandbookListView.as_view(), name='handbooks'),
    path('handbooks/<int:year>/<int:month>/<int:day>/', views.ActualHandbookListView.as_view(), name='actual_handbooks'),
    path('<str:handbook_name>/items/', views.HandbookItemListView.as_view(), name='handbook_items'),
]
