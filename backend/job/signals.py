from django.dispatch import receiver
from django.db.models.signals import post_save, post_migrate
from django.contrib.auth import get_user_model
User = get_user_model()


@receiver(post_migrate)
def create_super_user(sender, **kwargs):
    if User.objects.filter(email='admin@example.com').exists():
        pass
    else:
        User.objects.create_user(email='admin@example.com', password='admin', username='admin')
    

@receiver(post_migrate)
def create_test_user(sender, **kwargs):
    if User.objects.filter(email='test@example.com').exists():
        pass
    else:
        User.objects.create_user(email='test@example.com', password='test', username='test', is_superuser=False)
    