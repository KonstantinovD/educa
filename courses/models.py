from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField


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
    order = OrderField(blank=True, for_fields=['course'])
    # Новое поле называется order. Оно будет рассчитываться автоматически для каждого модуля в рамках одного курса,
    # т. к. мы указали for_fields=['course']. Таким образом, при создании нового
    # модуля его порядок будет больше на единицу, чем у предыдущего модуля курса.

    def __str__(self):
        return '{}. {}'.format(self.order, self.title)

    class Meta:
        ordering = ['order']
        # Теперь определим сортировку по умолчанию в классе Meta для моделей Module и Content:


class Content(models.Model):
    module = models.ForeignKey(Module,
                               related_name='contents',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={
                                         'model__in': (
                                             'text', 'video',
                                             'image', 'file'
                                         )})
    # Мы добавили атрибут limit_choices_to, чтобы ограничить типы содержимого ContentType, которые могут участвовать
    # в связи. Чтобы фильтровать объекты ContentType при запросах,
    # указали условие model__in и значения 'text', 'video', 'image' и 'file'.
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']

#     Это модель Content. Модуль курса может содержать множество объектов этого типа, поэтому мы используем ForeignKey
# на модель Module. Также мы выполнили обобщенную связь, чтобы соединить объекты типа Content с любой другой моделью,
# представляющей тип содержимого. Помните, чтобы обобщенные связи работали, нам необходимо создать три поля в модели:
# ...+ content_type – внешний ключ, ForeignKey, на модель ContentType;
# ...+ object_id – идентификатор связанного объекта типа PositiveIntegerField;
# ...+ item – поле типа GenericForeignKey, которое обобщает данные из предыдущих двух.
# Только поля content_type и object_id будут представлены в базе данных соответствующими столбцами.
# Поле item используется только в Python-коде и позволяет вам получить или задать связанный объект.


class ItemBase(models.Model):
    owner = models.ForeignKey(User,
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
# В этом фрагменте вы создали абстрактную модель ItemBase, задав в опциях класса Meta атрибут abstract=True.
# Она содержит четыре поля: owner, title, created и updated, – которые будут общими для всех дочерних моделей.
# Поле owner содержит данные пользователя, который создал объект. Так как в
# дочерних классах будет присутствовать это поле, необходимо задать related_name
# для каждого из них.
# Django задает связанное наименование related_name в виде %(class)s,
# но мы определили его как '%(class)s_related'. Таким образом, объекты каждой
# дочерней модели будут доступны по именам
# text_related, file_related, image_related и video_related.


class Text(ItemBase):
    content = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to='files')


class Image(ItemBase):
    file = models.FileField(upload_to='images')


class Video(ItemBase):
    url = models.URLField()
    # Мы применили поле URLField, чтобы сохранять URL видео для его скачивания.
