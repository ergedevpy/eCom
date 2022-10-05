from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from django.views.generic import DetailView, ListView

from .models import Item, OrderItem, Order, BillingAddress
from .forms import ShippingAddressForm


class HomeView(ListView):
    model = Item
    paginate_by = 12
    template_name = 'frontend/home.html'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'frontend/detail.html'

    # @method_decorator(login_required)
    # def dispatch(self, *args, **kwargs):
    #     return super(ItemDetailView, self).dispatch(*args, **kwargs)


@login_required(login_url='../account/login')
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_q = Order.objects.filter(user=request.user, ordered=False)

    if order_q.exists():
        order = order_q[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'Item added to your cart!')
            return redirect('frontend:summary')
        else:
            messages.info(request, 'Item added to your cart!')
            order.items.add(order_item)
            return redirect('frontend:summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, 'Item added to your cart!')
        return redirect('frontend:summary')


class OrderSummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            current_order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': current_order
            }
            return render(self.request, 'frontend/summary.html', context=context)
        except ObjectDoesNotExist:
            messages.warning(self.request, 'You do not have an active orders')
            return redirect('/')

        return render(self.request, 'frontend/summary.html', context=context)


@login_required(login_url='../account/login')
def remove_single_item(request, slug):
    item = get_object_or_404(Item, slug=slug)

    order_q = Order.objects.filter(user=request.user, ordered=False)

    if order_q.exists():
        order = order_q[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)

            messages.info(request, 'Cart updated')
            return redirect('frontend:summary')
        else:
            messages.warning(request, 'Item was not in your cart')
            return redirect('frontend:detail', slug=slug)
    else:
        messages.warning(request, 'You do not have an active order')
        return redirect('frontend:detail', slug=slug)


@login_required(login_url='../account/login')
def remove_item(request, slug):
    item = get_object_or_404(Item, slug=slug)

    order_q = Order.objects.filter(user=request.user, ordered=False)

    if order_q.exists():
        order = order_q[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)

            messages.info(request, 'Cart updated')
            return redirect('frontend:summary')

        else:
            messages.warning(request, 'Item was not in your cart')
            return redirect('frontend:detail', slug=slug)

    else:
        messages.warning(request, 'You do not have an active order')
        return redirect('frontend:detail', slug=slug)


class ShippingAddressView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = ShippingAddressForm()
            context = {
                'form': form,
                'order': order
            }
            return render(self.request, 'frontend/shipping-address.html', context=context)
        except ObjectDoesNotExist:
            messages.warning(self.request, 'You do not have an active order')
            return redirect('frontend:summary')

    def post(self, *args, **kwargs):
        form = ShippingAddressForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment = form.cleaned_data.get('apartment')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')

                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment=apartment,
                    country=country,
                    zip=zip
                )

                billing_address.save()
                order.billing_address = billing_address
                order.save()

                messages.info(self.request, 'Address added to order')

                return redirect('frontend:summary')
        except ObjectDoesNotExist:
            messages.warning(self.request, 'No active order')
            return redirect('frontend:summary')
