from django.contrib.auth.models import User
from django.db.models import query
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.views.decorators import csrf
from rest_framework import generics, permissions, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.db import IntegrityError
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from jists.models import Jist, Topic, Vote
from jists.serializers import JistSerializer, TopicSerializer, VoteSerializer


@csrf.csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            user = User.objects.create_user(data['username'], password=data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return JsonResponse({'token': str(token)}, status=201)
        except IntegrityError:
            return JsonResponse({'error': 'That username has already been taken. Please choose a different username.'})

@csrf.csrf_exempt
def login(request):
    if request.method == 'POST':
     
            data = JSONParser().parse(request)
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is None:
                return JsonResponse({'error': 'The username or password entered is incorrect. Please try again.'})
            else:
                try:
                    token = Token.objects.get(user=user)
                except:
                    token = Token.objects.create(user=user)
                return JsonResponse({'token': str(token)}, status=200)

@csrf.csrf_exempt
def logoutuser(request):
        logout(request)
        return redirect('/admin') 

class TopicList(generics.ListCreateAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TopicUpdate(generics.UpdateAPIView, mixins.RetrieveModelMixin):
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        topic = Topic.objects.get(pk=self.kwargs['pk'])
        return Topic.objects.filter(user=user, topic=topic)

class JistList(generics.ListCreateAPIView):
    queryset = Jist.objects.all().order_by('vote')
    serializer_class = JistSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)

class VoteCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        jist = Jist.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(voter=user, jist=jist)

    def perform_create(self, serializer):
        if self.get_queryset().exists():
            raise ValidationError('This user has already voted for this post.')
        serializer.save(voter=self.request.user, jist=Jist.objects.get(pk=self.kwargs['pk']))

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status = status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('This user has never voted for this post.')

