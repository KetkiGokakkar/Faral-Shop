# shop/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    if created:
        # For MVP: simple log. Replace with actual notifier (Twilio/WhatsApp/FCM) or Celery task.
        print(f"[NOTIFY] New order created: {instance.id} for {instance.customer.phone}")
        # in future: enqueue a background task to send SMS/WhatsApp
