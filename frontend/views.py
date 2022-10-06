from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from django.views.generic import DetailView, ListView

from .models import Item, OrderItem, Order, BillingAddress, Coupon, Payment
from .forms import ShippingAddressForm, CouponForm

import stripe
import random
import string
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_order_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))


class HomeView(ListView):
    model = Item
    paginate_by = 8
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


class ShippingAddressView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = ShippingAddressForm()
            context = {
                'form': form,
                'order': order,
                'couponform': CouponForm(),
                'display_coupon_form': True
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


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.warning(request, "This coupon is not valid")
        # return redirect('frontend:shipping-address')
        return None


class CouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                if get_coupon(self.request, code):
                    order.coupon = get_coupon(self.request, code)
                    order.save()
                    messages.success(self.request, "Coupon added")

                return redirect('frontend:shipping-address')

            except ObjectDoesNotExist:
                messages.success(self.request, "You do not have an active order")
                return redirect('frontend:shipping-address')


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'display_coupon_form': False
            }
            return render(self.request, 'frontend/payment.html', context)
        else:
            messages.warning(self.request, 'Please add your billing address')
            return redirect('frontend:shipping-address')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.total_price() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency='usd',
                source=token,
                description='Payment from ecommerce-django'
            )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.total_price()
            payment.save()

            order_items = order.items.all()
            order_items.update(ordered=True)

            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment

            order.order_ref = create_order_code()
            order.save()

            messages.success(self.request, 'Oredered successful')
            return redirect('/')

        except stripe.error.CardError as e:

            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/")
        except stripe.error.RateLimitError as e:
            messages.warning(self.request, "Rate Limit Error")
            return redirect("/")
        except stripe.error.InvalidRequestError as e:
            messages.warning(self.request, "Invalid parameters")
            print("Invalid parameters", e)
            print("the value is: ", amount)
            return redirect("/")
        except stripe.error.AuthenticationError as e:
            messages.warning(self.request, "Not authenticated")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            messages.warning(self.request, "Network Error")
            return redirect("/")
        except stripe.error.StripeError as e:
            print(e)
            messages.warning(self.request, "Something went wong, you were not charged, please try again!")
            return redirect("/")
        except Exception as e:
            print(e)
            messages.warning(self.request, "Something went wong, we will work about it since we have been notified.")
            return redirect("/")
