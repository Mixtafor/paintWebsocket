import random
import string

from django.core.mail import send_mail
from django.core.cache import cache
from django import forms
from django.shortcuts import render

from main.models import Chat, User, Message


def get_all_msgs(chat_id):
    chat = Chat.objects.prefetch_related('messages__sender').get(id=chat_id)
    messages = chat.messages.all()
    return [[msg.sender.get_full_name(), msg.sender.avatar.url, msg.message, msg.pk, msg.sender.pk] for msg in messages]


def add_new_message_to_chat(message: str, user: User, chat_id: str):
    message = Message.objects.create(message=message, sender=user)
    chat = Chat.objects.get(id=chat_id)
    chat.messages.add(message)
    chat.save()
    return message


def delete_message_from_chat(msg_pk: str, chat_id: str):
    message = Message.objects.get(id=msg_pk)
    chat = Chat.objects.get(id=chat_id)
    chat.messages.remove(message)
    chat.save()
    message.delete()


def generic_random_str(length: int) -> str:
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])


def verify_email(data: dict):  # TODO: func check email with celery
    path_id = generic_random_str(10)
    cache.set(path_id, data, 60 * 4)
    subject = 'Verify your email'
    message = 'Refer to the path to verify your email: http://127.0.0.1:8000/check_email?id=%s' % path_id
    send_mail(
        subject=subject,
        message=message,
        recipient_list=[data['email']],
        from_email='Mikstafor0@yandex.ru'
    )


def check_email_for_uniq(email: str) -> bool:
    return False if email in [i.email for i in User.objects.only('email').all()] else True


def get_form_object(user, *args, **kwargs):
    # return form object
    class PersonDataForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ('first_name', 'last_name')

        first_name = forms.CharField(max_length=25, widget=forms.TextInput(attrs={'value': user.first_name}))
        last_name = forms.CharField(max_length=25,
                                    widget=forms.TextInput(attrs={'value': user.last_name}))

    return PersonDataForm(*args, **kwargs)


def get_owner_user_profile(user, request):
    if request.method == 'POST':
        form = get_form_object(user, request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

    form = get_form_object(user)
    return render(request, 'main/owner_profile.html', {"profile": user,
                                                       "form": form})
