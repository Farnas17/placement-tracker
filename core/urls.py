from django.urls import path
from .views import task_list_create, update_task
from .views import dashboard_summary
from .views import dashboard_page 
from .views import tasks_page
from .views import api_login
from django.views.generic import RedirectView

urlpatterns = [
    path('api/tasks/', task_list_create),
    path('api/tasks/<int:pk>/', update_task),
    path('dashboard/', dashboard_summary),
    path('dashboard-ui/', dashboard_page, name='dashboard-ui'),
    path('api/dashboard/', dashboard_summary),
    path('tasks-ui/', tasks_page, name='tasks-ui'),
    path('api/login/', api_login),
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),
]