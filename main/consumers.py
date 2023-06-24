# import json
#
# from asgiref.sync import sync_to_async
# from channels.db import database_sync_to_async
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.contrib.auth.models import AnonymousUser
# from django.contrib.sessions.models import Session
#
# from main.models import User, Message, Chat
# from main.services.services import delete_message_from_chat
# from django.core.cache import cache
#
#
# @database_sync_to_async
# def get_chat_users(chat_id, user):
#     return [i for i in Chat.objects.get(id=chat_id).users.all() if i != user]
#
#
# @database_sync_to_async
# def get_chat_user(chat_id, user):
#     return [i for i in Chat.objects.get(id=chat_id).users.all() if i != user][0].pk
#
#
# @database_sync_to_async
# def get_user(user_session_id):
#     try:
#         s = Session.objects.get(session_key=user_session_id)
#         return User.objects.get(id=s.get_decoded()['_auth_user_id'])
#     except User.DoesNotExist:
#         return AnonymousUser()
#
#
# async def a_add_new_message_to_chat(message: str, user: User, chat_id: str):
#     message = await Message.objects.acreate(message=message, sender=user)
#     chat = await Chat.objects.aget(id=chat_id)
#     await sync_to_async(chat.messages.add)(message)
#     # chat.messages.add(message)  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#     await sync_to_async(chat.save)()
#     return message
#
#
# @database_sync_to_async
# def info(user_id, message: Message):
#     user = User.objects.get(id=user_id)
#     return [user.get_full_name(), user.avatar.url, message.message, message.pk, message.sender.pk, False]
#
#
# @database_sync_to_async
# def get_message_sender(msg_id):
#     return Message.objects.get(id=msg_id).sender
#
#
# @database_sync_to_async
# def get_all_interlocutors(user):
#     return [[i for i in chat.users.all() if i != user][0] for chat in user.chat_set.all()]
#
#
# class AsyncChatConsumer(AsyncWebsocketConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(args, kwargs)
#         self.user = None
#
#     async def connect(self):
#         # self.user = await get_user(int(self.scope['url_route']['kwargs']['user_session_id']))
#         self.user = self.scope['user']
#         if not isinstance(self.user, AnonymousUser):
#             user_pk = str(self.user.pk)
#             await cache.aset(user_pk, True, 60 * 60 * 24)
#             for person in await get_all_interlocutors(self.user):
#                 await self.channel_layer.group_send(str(person.pk), {
#                     'type': 'online_status_message',
#                     'action': 'online_status',
#                     'user': str(self.user.pk),
#                     'status': 'online',
#                 })
#             await self.channel_layer.group_add(user_pk, self.channel_name)
#             await self.accept()
#
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#
#         if text_data_json['action'] == 'post':
#             message = text_data_json["message"]
#             chat_id = text_data_json['chat_id']
#
#             to_user_id = await get_chat_user(chat_id, self.user)
#             # user = await User.objects.aget(id=from_user_id)
#
#             message = await a_add_new_message_to_chat(
#                 message=message,
#                 user=self.user,
#                 chat_id=chat_id
#             )
#
#             await self.send(json.dumps({"action": "post",
#                                         "msgs": [await self.user.aget_full_name(),
#                                                  self.user.avatar.url,
#                                                  message.message,
#                                                  message.pk, message.sender.pk, True, False]}))
#
#             await self.channel_layer.group_send(
#                 str(to_user_id),
#                 {
#                     "type": "chat_message",
#                     "text_data": text_data,
#                     'message_id': message.pk,
#                     'from_user_id': self.user.pk
#                 }
#             )
#         elif text_data_json['action'] == 'delete':
#             if self.user == await get_message_sender(text_data_json['msg_id']):
#                 await self.send(json.dumps({
#                     "action": 'delete',
#                     'msg_id': text_data_json['msg_id'],
#                     'chat_id': text_data_json['chat_id'],
#                 }))
#                 chat_users = await get_chat_users(text_data_json['chat_id'], self.user)
#                 for user in chat_users:
#                     await self.channel_layer.group_send(str(user.pk),
#                                                         {
#                                                             'type': 'del_message',
#                                                             'chat_id': text_data_json['chat_id'],
#                                                             'msg_id': text_data_json['msg_id']
#                                                         })
#                 await sync_to_async(delete_message_from_chat)(text_data_json['msg_id'], text_data_json['chat_id'])
#
#         elif text_data_json['action'] == 'update_is_viewed_status':
#             chat_id = text_data_json['chat_id']
#             chat = await Chat.objects.prefetch_related('messages__sender').aget(id=chat_id)
#             messages = await sync_to_async(chat.messages.all)()
#             data = []
#             for msg in messages:
#                 if msg.sender != self.user and msg.is_viewed is False:
#                     msg.is_viewed = True
#                     await sync_to_async(msg.save)()
#                     data.append(msg)
#             try:
#                 await self.channel_layer.group_send(
#                     str(data[0].sender.pk),
#                     {
#                         'type': 'update_is_viewed_status',
#                         'msgs': [msg.pk for msg in data],
#                     }
#                 )
#             except IndexError:
#                 pass
#
#     async def chat_message(self, event):
#
#         message = await Message.objects.aget(id=event['message_id'])
#
#         await self.channel_layer.group_send(str(event['from_user_id']), {
#             'type': 'update_is_viewed_status',
#             'msgs': [event['message_id']],
#         })
#         await self.send(json.dumps({"action": "post",
#                                     "msgs": await info(event['from_user_id'], message)}))
#
#     async def del_message(self, event):
#         await self.send(json.dumps({
#             "action": 'delete',
#             'msg_id': event['msg_id'],
#             'chat_id': event['chat_id'],
#         }))
#
#     async def disconnect(self, code):
#         for person in await get_all_interlocutors(self.user):
#             await self.channel_layer.group_send(str(person.pk), {
#                 'type': 'online_status_message',
#                 'action': 'online_status',
#                 'user': str(self.user.pk),
#                 'status': 'offline',
#             })
#
#         await cache.adelete(self.user.pk)
#         await self.channel_layer.group_discard(str(self.user.pk), self.channel_name)
#
#     async def online_status_message(self, event):
#         await self.send(json.dumps({
#             'action': 'online_status',
#             'user': event['user'],
#             'status': event['status']
#         }))
#
#     async def update_is_viewed_status(self, event):
#         await self.send(json.dumps({
#             'action': 'update_is_viewed_status',
#             'msgs': event['msgs'],
#         }))
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class AsyncChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room = None

    async def connect(self):
        self.room = str(self.scope['url_route']['kwargs'].get('id'))
        # print(self.scope)
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        if text_data_json['action'] == 'coord':
            await self.channel_layer.group_send(
                self.room,
                {
                    'type': 'room_msg',
                    'x': text_data_json['x'],
                    'y': text_data_json['y']
                }
            )
        elif text_data_json['action'] == 'is_mouse_down':
            await self.channel_layer.group_send(
                self.room,
                {
                    'type': 'is_mouse_msg',
                    'status': text_data_json['status'],
                }
            )

    async def room_msg(self, event):
        await self.send(json.dumps({'action': 'coord', 'x': int(event['x']), 'y': int(event['y'])}))

    async def is_mouse_msg(self, event):
        await self.send(json.dumps({'action': 'is_mouse_down', 'status': event['status']}))
