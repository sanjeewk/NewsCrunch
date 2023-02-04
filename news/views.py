from django.shortcuts import render
from django.utils.dateformat import DateFormat
# from datetime import datetime, date
import datetime
from django.utils import timezone
# Create your views here.
from django.views.generic import ListView

from .models import Article

class HomePageView(ListView):
    template_name = "articles.html"
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["articles"] = Article.objects.filter().order_by("-pub_date")[:12]
        today = datetime.date.today()

        context["summary"] = Article.objects.filter(pub_date__date=today)
        context["summary"] = Article.objects.filter().order_by("-pub_date")[:5]
        summaries = []
        for article in context["summary"]:
            line = article.title + ". " + article.summarised_text
            summaries.append(line)
        context["summaries"] = summaries
        d = datetime.datetime.now()
        df = DateFormat(d)
        date = df.format('F jS Y')
        context["date"] = str(date)
        print(date)
        return context

