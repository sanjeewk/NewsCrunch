from django.shortcuts import render
from django.utils.dateformat import DateFormat
from datetime import datetime
# Create your views here.
from django.views.generic import ListView

from .models import Article

class HomePageView(ListView):
    template_name = "articles.html"
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["articles"] = Article.objects.filter().order_by("-pub_date")[:21]
        d = datetime.now()
        df = DateFormat(d)
        date = df.format('F jS Y')
        context["date"] = str(date)
        print(date)
        return context

