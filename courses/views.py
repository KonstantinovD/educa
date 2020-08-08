from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Course
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin


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


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
                             data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})
# Класс CourseModuleUpdateView обрабатывает действия, связанные с набором форм по сохранению, редактированию и удалению
# модулей для конкретного курса. Этот обработчик наследуется от таких классов:
#   - TemplateResponseMixin – примесь, которая добавит формирование HTML-шаблона и вернет его в качестве ответа
#   на запрос. Она использует шаблон, имя которого задано в атрибуте template_name, и добавляет в дочерние классы метод
#   render_to_response(), который сформирует результирующую страницу;
#   - View – базовый класс для обработчиков Django. В этом обработчике мы описали четыре метода:
#     1) get_formset() – метод, позволяющий избежать дублирования кода, который отвечает за формирование набора форм;
#     2) dispatch() – метод, определенный в базовом классе View. Он принимает объект запроса и его параметры и пытается
#     вызвать метод, который соответствует HTTP-методу запроса. Если запрос отправлен с помощью GET, его обработка будет
#     делегирована методу get() обработчика; если POST – то методу post(). Внутри функции мы пытаемся получить объект
#     типа Course с помощью get_object_or_404(), т. к. курс необходим как для GET-так и для POST-запросов, а затем
#     сохраняем его в атрибут класса course;
#     3) get() – метод, обрабатывающий GET-запрос. Мы создаем пустой набор форм ModuleFormSet и отображаем его в шаблоне
#     с данными курса, используя для этого метод родительского класса render_to_response();
#     4) post() – метод, обрабатывающий POST-запросы. При этом выполняются следующие шаги:
#       - создается набор форм ModuleFormSet по отправленным данным;
#       - происходит проверка данных с помощью метода is_valid() набора форм;
#       - если все формы заполнены корректно, сохраняем объекты, вызвав метод save(). На этом этапе в базу данных будут
#       сохранены не только данные курса, но и все изменения модулей. Затем перенаправляем пользователя на страницу по
#       URL 'manage_course_list'. Если хотя бы одна форма набора заполнена некорректно, формируем страницу
#       с отображением ошибок.


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):  # возвращает класс модели по переданному имени. Допустимые значения – Text, Video,
        # Image и File. Мы обращаемся к модулю apps Django, чтобы получить класс модели.
        # Если его не удалось найти по переданному имени, возвращаем None
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):  # создает форму в зависимости от типа содержимого с помощью
        # функции modelform_factory(). Так как модели Text, Video, Image и File содержат общие поля, исключим их из
        # формы, чтобы пользователь заполнял только поле непосредственного содержимого (файл, текст, картинку или видео)
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):  # получает приведенные ниже данные из запроса
        # и создает соответствующие объекты модуля, модели содержимого:
        #   - module_id – идентификатор модуля, к которому привязано содержимое;
        #   - model_name – имя модели содержимого;
        #   - id – идентификатор изменяемого объекта.
        self.module = get_object_or_404(Module,
                                        id=module_id,
                                        course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id,
                                         owner=request.user)
        return super(ContentCreateUpdateView, self)\
            .dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        # извлекает из GET-параметров запроса данные. Формирует модельные формы для объектов Text, Video, Image
        # или File, если объект редактируется, т.е. указан self.obj. В противном случае мы отображаем пустую
        # форму для создания объекта
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):  # обрабатывает данные POST-запроса, для чего создает
        # модельную форму и валидирует ее. Если форма заполнена корректно, создает новый объект, указав текущего
        # пользователя, request.user, владельцем. Если в запросе был передан ID, значит, объект изменяют, а не создают
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # Создаем новый объект.
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)
# Обработчик ContentDeleteView получает объект типа Content по переданному ID и удаляет соответствующий объект модели
# Text, Video, Image или File, после чего ликвидирует объект Content. При успешном завершении действия перенаправляет
# пользователя на страницу по URLʼу с именем module_content_list.


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'
    # обработчик ModuleContentListView. Он получает из базы данных модуль по
    # переданному ID и генерирует для него страницу подробностей.

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    # Нам нужен обработчик, который будет получать новый порядок модулей курса в формате JSON
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                                  course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    # аналогичный обработчик для содержимого модулей
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                                   module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})
