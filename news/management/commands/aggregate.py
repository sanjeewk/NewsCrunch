# Standard Library
import logging
from os import link
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
# Django
from django.conf import settings
from django.core.management.base import BaseCommand
import json
# Third Party
import feedparser
from dateutil import parser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

# Models
from news.models import Article
from news import scrape

import requests
from news.summarization import Summariser
logger = logging.getLogger(__name__)
tokenizer = AutoTokenizer.from_pretrained("mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization")
model = AutoModelForSeq2SeqLM.from_pretrained("mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization")


def save_new_article(data, source):
    """saves article to database"""
    article = Article(
        title=data["title"],
        summarised_text=data['text'],
        pub_date=data['publishedAt'],
        link=data['url'],
        author=data['author'],
        publisher=source
    )
    article.save()

def delete_old_job_executions(max_age=604_800):
    """Deletes all apscheduler job execution logs older than `max_age`."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

def fetch_reuters_articles():
    summary = Summariser()
    print("fetchhhhhh")
    query_params = {
    "source" : "reuters",
    "sortBy" : "top",
    "apiKey" : "f58a31b8ccdb449f8bf038a5fac6282e",
    }
    main_url = " https://newsapi.org/v1/articles"
    
    # fetching data in json format
    res = requests.get(main_url, params=query_params)
    reuters_data = res.json()
    # print(json.dumps(reuters_data))
    if "articles" not in reuters_data:
        print("no articles")
        return
    headlines= reuters_data["articles"][:7]
    for headline in headlines:
        # print(headline['url'])
        # try:
        if Article.objects.filter(title=headline["title"]).exists() and "Explainer:" not in headline["title"]:
            article = scrape.get_reuters_text(headline['url'])
            article = " ".join(article)
            headline['text'] = summary(article)
            
            save_new_article(headline, source="Reuters")
        # except:
        #     print("article unable")

# def fetch_ap_articles():
#     query_params = {
#     "source": "associated-press",
#     "sortBy": "top",
#     "apiKey": "f58a31b8ccdb449f8bf038a5fac6282e"
#     }
#     main_url = " https://newsapi.org/v1/articles"

#     # fetching data in json format
#     res = requests.get(main_url, params=query_params)
#     ap_data = res.json()

#     headlines= ap_data["articles"][:5]

#     for headline in headlines:
#         # print(headline['url'])
#         # try:
#         if not Article.objects.filter(title=headline["title"]).exists():
#             article = scrape.get_ap_text(headline['url'])

#             article = " ".join(article)
#             txt = summarization.extractive_summary(article)

#             print("-----------------------")
#             print("AP ", txt)
#             txt = sum(str(txt))[0]

#             # print(txt)
#             headline['text'] = txt['summary_text']
#             save_new_article(headline, source="ap")
#         # except:
#         #     print("article unable")
        # print(headline)



class Command(BaseCommand):
    help = "Runs apscheduler."
    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout, stderr, no_color)
        self.summary = Summariser()
            # args=[(self.summary)],
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        scheduler.add_job(
            fetch_reuters_articles,
            # trigger = CronTrigger(year="*", month="*", day="*", hour="13", minute="0"),
            trigger="interval",
            minutes=2,
            id="Reuters articles",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Fetch Reuters Feed.")

        # scheduler.add_job(
        #     fetch_ap_articles,
        #     trigger="interval",
        #     minutes=2,
        #     id="AP articles",
        #     max_instances=1,
        #     replace_existing=True,
        # )

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="Delete Old Job Executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: Delete Old Job Executions.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
