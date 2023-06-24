# from Tools.demo.mcast import sender
# from django.db.models.signals import m2m_changed
# from django.dispatch import receiver
#
# from main.models import User
#
#
# @receiver(m2m_changed, sender=User.liked_comments.through)
# @receiver(m2m_changed, sender=User.liked_photos.through)
# def liked_comments_or_liked_photos_changed(sender, **kwargs):
#     if kwargs['action'] == 'pre_remove':
#         objs = kwargs['model'].objects.filter(pk__in=kwargs['pk_set'])
#         for obj in objs:
#             obj.likes -= 1
#             obj.save()
#     elif kwargs['action'] == 'pre_add':
#         objs = kwargs['model'].objects.filter(pk__in=kwargs['pk_set'])
#         for obj in objs:
#             obj.likes += 1
#             obj.save()
