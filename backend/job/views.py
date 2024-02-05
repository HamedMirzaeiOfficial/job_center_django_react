from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Job, Request
from .serializers import JobSerializer, RequestSerializer
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
    

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

class Login(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            # Ensure that 'is_superuser' is added to the payload
            payload = {
                'user_id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser,  # Add is_superuser claim
            }
            token = jwt_encode_handler(payload)
            return Response({'token': token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@permission_classes([permissions.IsAuthenticated])
@authentication_classes([JSONWebTokenAuthentication])
class JobListCreateAPIView(APIView):
    def get(self, request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@permission_classes([permissions.IsAuthenticated])
@authentication_classes([JSONWebTokenAuthentication])
class JobDetailAPIView(APIView):
    def get_job(self, pk):
        try:
            return Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    @method_decorator(cache_page(60 * 15))
    def get(self, request, pk):
        job = self.get_job(pk)
        serializer = JobSerializer(job)
        return Response(serializer.data)

    def put(self, request, pk):
        job = self.get_job(pk)
        serializer = JobSerializer(job, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        job = self.get_job(pk)
        job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class RequestSendAPIView(APIView):
    def get_job(self, pk):
        try:
            return Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
        
    def post(self, request, pk):
        job = self.get_job(pk)

        # Create a Request object
        request_data = {'job': job.id, 'user': self.request.user.id, 'resume': request.FILES.get('resume')}
        request_serializer = RequestSerializer(data=request_data)

        if request_serializer.is_valid():
            request_instance = request_serializer.save()
            return Response({'message': 'Request sent successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid request data'}, status=status.HTTP_400_BAD_REQUEST)


class JobRequestsListAPIView(generics.ListAPIView):
    serializer_class = RequestSerializer

    def get_queryset(self):
        job_id = self.kwargs['pk']
        return Request.objects.filter(job__id=job_id)