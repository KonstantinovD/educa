from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)
# В этом фрагменте мы определили две примеси: OwnerMixin и OwnerEditMixin. Они будут добавлены к нашим обработчикам
# вместе с такими классами Django, как ListView, CreateView, UpdateView и DeleteView. Примесь OwnerMixin определяет
# метод get_queryset(). Он используется для получения базового QuerySetʼа, с которым будет работать обработчик.
# Мы переопределили этот метод, так чтобы получать только объекты,
# владельцем которых является текущий пользователь (request.user).


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)
# Примесь OwnerEditMixin определяет метод form_valid(). Django вызывает его для обработчиков, которые наследуются
# от ModelFormMixin и работают с формами и модельными формами, например CreateView или UpdateView. Методы выполняются,
# когда форма успешно проходит валидацию. Поведение по умолчанию для примеси Django – сохранение объекта в базу данных
# (для модельных форм) и перенаправление пользователя на страницу по адресу success_url (для обычных форм).
# Мы переопределили этот метод, чтобы автоматически заполнять поле owner сохраняемого объекта.
# Примесь OwnerMixin можно применять для любого обработчика, который работает с моделью, содержащей поле owner.


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')
# Мы также создали класс OwnerCourseMixin, который наследуется от OwnerMixin,
# и добавили для него атрибут model – модель, с которой работает обработчик.


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')
    template_name = 'courses/manage/course/form.html'
# Еще одна примесь, OwnerCourseEditMixin, содержит такие атрибуты:
#    - fields – поля модели, из которых будет формироваться объект обработчиками CreateView и UpdateView;
#    - success_url – адрес, на который пользователь будет перенаправлен после успешной обработки формы
# классами CreateView и UpdateView или их наследниками.
# Мы указали шаблон URLʼа с именем manage_course_list, который добавим чуть позже.


class ManageCourseListView(OwnerCourseMixin, ListView):  # список курсов, созданных пользователем
    template_name = 'courses/manage/course/list.html'


class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin,
                       CreateView):  # использует модельную форму для создания нового курса.
    # При создании объекта из данных запроса учитывает поля, определенные в родительском классе OwnerCourseEditMixin
    permission_required = 'courses.add_course'
    # Примесь PermissionRequiredMixin добавляет проверку наличия у
    # пользователя разрешения, указанного в атрибуте permission_required


class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin,
                       UpdateView):  # позволяет владельцу курса редактировать его
    permission_required = 'courses.change_course'


class CourseDeleteView(PermissionRequiredMixin, OwnerCourseMixin,
                       DeleteView):  # Задает атрибут success_url – адрес, на который пользователь
    # будет перенаправлен после успешного удаления объекта
    template_name = 'courses/manage/course/delete.html'
    success_url = reverse_lazy('manage_course_list')
    permission_required = 'courses.delete_course'
