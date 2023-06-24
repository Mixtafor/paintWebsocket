import json

from django.contrib.auth import login
import django.middleware.csrf
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render


from main.models import User, Room


def main(request):
    return render(request, 'main/index.html')


# @login_required('login')
def create(request):
    # cache.set(request.user.pk, [request.user.pk], 60 * 60 * 2)
    room = Room.objects.create(room_id=request.user.pk)
    room.members.set([request.user])
    room.save()
    return JsonResponse({'users': [request.user.pk]})


def register(request: HttpRequest):
    data: dict = json.loads(request.body.decode('utf-8'))
    user = User.objects.create(
        email=data['email'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data['last_name'],
    )
    user.save()
    login(request, user)
    resp = JsonResponse({'user_id': user.pk})
    return resp


def get_csrf(request):
    token = django.middleware.csrf.get_token(request)
    print(token)
    return JsonResponse({'csrf_token': token})


def rooms(request):
    return JsonResponse({'rooms': [room.room_id for room in Room.objects.all()]})


def connect(request):
    room_id = request.GET.get('id')
    room = Room.objects.get(room_id=room_id)
    return JsonResponse({'users': [user.pk for user in room.members.all()]})
