from django.db import models


# Modals for Articles app

class User(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=200)
    pswd = models.CharField(max_length=200)
    is_admin = models.BooleanField(default=False)
    status = models.BooleanField(default=False)

    @staticmethod
    def get_user_by_username(username):
        try:
            return User.objects.get(username=username)
        except:
            return False

    def __str__(self):
        return self.username


class Article(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    area = models.CharField(max_length=200)
    abstract = models.TextField()

    @staticmethod
    def get_article_by_pk(pk):
        try:
            return Article.objects.get(id=pk)
        except:
            return False

    def __str__(self):
        return self.title
