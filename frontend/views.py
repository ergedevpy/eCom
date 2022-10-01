from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import Item


# def home(request):
#     context = {
#         'items': Item.objects.all()
#     }
#
#     return render(request, 'frontend/home.html', context=context)


class HomeView(ListView):
    model = Item
    paginate_by = 12
    template_name = 'frontend/home.html'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'frontend/detail.html'
