from django import template
from django.contrib.auth.models import User

from frontend.models import Order

register = template.Library()


@register.filter
def cart_count(user: User):
    if user.is_authenticated:
        query_set = Order.objects.filter(user=user, ordered=False)

        if query_set.exists():
            return query_set[0].items.count()
        return 0
