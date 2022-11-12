from django.db import models

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=200)
    summarised_text = models.TextField()
    pub_date = models.DateTimeField()
    link = models.URLField()
    author = models.CharField(max_length=100, null=True) 
    publisher = models.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return f"{self.publisher}: {self.title}"
