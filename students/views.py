from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseEnrollForm
from django.views.generic.list import ListView
from courses.models import Course
from django.views.generic.detail import DetailView


class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')

    def form_valid(self, form):
        result = super(StudentRegistrationView, self).form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result
# Это обработчик регистрации студентов на сайте. Мы используем специальный класс CreateView, который предоставляет
# методы создания объектов заданной модели. Также мы определяем несколько атрибутов модели:
#   - template_name – имя HTML-шаблона, который будет использоваться;
#   - form_class – класс формы для создания объекта. Указанный класс должен быть наследником ModelForm. Мы указали форму
#   UserCreationForm для создания объектов модели User;
#   - success_url – адрес, на который пользователь будет перенаправлен после успешной обработки формы регистрации.
#   Мы получаем URL по имени student_course_list, но создадим его чуть позже.
# Метод form_valid() обработчика будет выполняться при успешной валидации формы. Он должен возвращать объект
# HTTP-ответа. Мы переопределили его в нашем обработчике, чтобы после регистрации автоматически авторизовать
# пользователя на сайте.


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm
    # Это обработчик StudentEnrollCourseView. Он занимается зачислением студентов на курсы. Мы указали родительский
    # класс LoginRequiredMixin, поэтому только авторизованные пользователи смогут записываться. Также родительским
    # классом является базовый обработчик Django, FormView, который реализует работу с формой. В атрибуте form_class
    # мы указали форму CourseEnrollForm, которая при успешной валидации будет создавать связь между студентом и курсом

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super(StudentEnrollCourseView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_course_detail', args=[self.course.id])


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    def get_queryset(self):
        qs = super(StudentCourseListView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])
# Этот обработчик будет формировать список курсов, слушателем которых является студент. Мы используем примесь
# LoginRequiredMixin, чтобы только авторизованные пользователи могли иметь доступ к этой странице. Наш обработчик также
# наследуется от класса ListView, чтобы отображать объекты модели Course в виде списка. Чтобы получить только курсы,
# связанные с текущим пользователем, мы переопределили метод get_queryset() и отфильтровали QuerySet курсов по связи
# ManyToManyField со студентом.


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super(StudentCourseDetailView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super(StudentCourseDetailView, self).get_context_data(**kwargs)
        # Получаем объект курса.
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # Получаем текущий модуль по параметрам запроса.
            context['module'] = course.modules.get(id=self.kwargs['module_id'])
        else:
            # Получаем первый модуль.
            context['module'] = course.modules.all()[0]
        return context
# Это обработчик StudentCourseDetailView. Мы переопределили метод get_queryset(), чтобы ограничить QuerySet курсов
# и работать только с теми, на которые записан текущий пользователь. Мы также переопределили метод get_context_data(),
# чтобы добавить в контекст шаблона данные о модуле, если его идентификатор был передан в параметре module_id URLʼа.
# В противном случае мы показываем содержимое первого модуля. Так студенты смогут переходить от одного модуля курса
# к другому.
