from django.urls import path
from .views import JobListCreateAPIView, Login, JobDetailAPIView, RequestSendAPIView, JobRequestsListAPIView

urlpatterns = [
    path('login/', Login.as_view(), name='login'),  
    path('jobs/all/', JobListCreateAPIView.as_view(), name='job-list-api'),
    path('jobs/', JobListCreateAPIView.as_view(), name='job-list-api'),  # Updated URL
    path('job_detail/<int:pk>/', JobDetailAPIView.as_view(), name='job-detail-api'),
    path('job_detail/<int:pk>/send_request/', RequestSendAPIView.as_view(), name='job-send-request-api'), 
    path('job_detail/<int:pk>/requests/', JobRequestsListAPIView.as_view(), name='job-requests-api'),
]

