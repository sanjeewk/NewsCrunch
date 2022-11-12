# Standard Library
import logging
from os import link
#TODO 
# Django
from django.conf import settings
from django.core.management.base import BaseCommand

# Third Party
import feedparser
from dateutil import parser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

# Models
from podcasts.models import Episode
from news.models import Article
from news import scrape

import requests
import news.summarization as summarization
logger = logging.getLogger(__name__)


def save_new_episodes(feed):
    """Saves new episodes to the database.

    Checks the episode GUID agaist the episodes currently stored in the
    database. If not found, then a new `Episode` is added to the database.

    Args:
        feed: requires a feedparser object
    """
    podcast_title = feed.channel.title
    podcast_image = feed.channel.image["href"]

    for item in feed.entries:
        if not Episode.objects.filter(guid=item.guid).exists():
            episode = Episode(
                title=item.title,
                description=item.description,
                pub_date=parser.parse(item.published),
                link=item.link,
                image=podcast_image,
                podcast_name=podcast_title,
                guid=item.guid,
            )
            episode.save()

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

def fetch_realpython_episodes():
    """Fetches new episodes from RSS for the Real Python Podcast."""
    _feed = feedparser.parse("https://realpython.com/podcasts/rpp/feed")
    save_new_episodes(_feed)



def delete_old_job_executions(max_age=604_800):
    """Deletes all apscheduler job execution logs older than `max_age`."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

def fetch_reuters_episodes():
    query_params = {
    "source": "reuters",
    "sortBy": "top",
    "apiKey": "f58a31b8ccdb449f8bf038a5fac6282e"
    }
    main_url = " https://newsapi.org/v1/articles"

    # fetching data in json format
    res = requests.get(main_url, params=query_params)
    reuters_data = res.json()

    headlines= reuters_data["articles"]

    for headline in headlines:
        print(headline['url'])
        try:
            article = scrape.get_reuters_text(headline['url'])
            article = " ".join(article)
            # print(summarization.abstract_summary(a))
            txt = summarization.abstract_summary(article)
            headline['text'] = txt
        except:
            print("article unable")
        print(headline)
        save_new_article(headline, source="reuters")


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # scheduler.add_job(
        #     fetch_realpython_episodes,
        #     trigger="interval",
        #     minutes=2,
        #     id="The Real Python Podcast",  # Each job MUST have a unique ID
        #     max_instances=1,
        #     # Replaces existing and stops duplicates on restart of the app.
        #     replace_existing=True,
        # )
        # logger.info("Added job: The Real Python Podcast.")

        scheduler.add_job(
            fetch_reuters_episodes,
            trigger="interval",
            minutes=1,
            id="Talk Python Feed",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Reuters Feed.")

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