from django.urls import path

from .views import handbook_list, actual_handbook, current_version_handbook_items, \
    specified_version_handbook_items


app_name = 'test_task'
urlpatterns = [
    path('handbooks/', handbook_list, name='handbooks'),
    path('handbook/<int:year>/<int:month>/<int:day>/', actual_handbook, name='actual_handbook'),
    path('handbook/items', current_version_handbook_items, name='current_handbook_items'),
    path('handbook/<str:version>/items', specified_version_handbook_items, name='handbook_items'),
]
