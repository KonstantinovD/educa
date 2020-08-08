from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(User, related_name='courses_created',
                              on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, related_name='courses',
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules',
                               on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Content(models.Model):
    module = models.ForeignKey(Module,
                               related_name='contents',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
#     Это модель Content. Модуль курса может содержать множество объектов этого типа, поэтому мы используем ForeignKey
# на модель Module. Также мы выполнили обобщенную связь, чтобы соединить объекты типа Content с любой другой моделью,
# представляющей тип содержимого. Помните, чтобы обобщенные связи работали, нам необходимо создать три поля в модели:
# ...+ content_type – внешний ключ, ForeignKey, на модель ContentType;
# ...+ object_id – идентификатор связанного объекта типа PositiveIntegerField;
# ...+ item – поле типа GenericForeignKey, которое обобщает данные из предыдущих двух.
# Только поля content_type и object_id будут представлены в базе данных соответствующими столбцами.
# Поле item используется только в Python-коде и позволяет вам получить или задать связанный объект.
