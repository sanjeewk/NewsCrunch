# Generated by Django 3.2.6 on 2022-11-04 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_article_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='author',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='publisher',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
