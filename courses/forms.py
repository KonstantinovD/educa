from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module


ModuleFormSet = inlineformset_factory(Course,
                                      Module,
                                      fields=['title', 'description'],
                                      extra=2,
                                      can_delete=True)
# Это набор форм ModuleFormSet. Мы формируем его с помощью фабричной функции Django inlineformset_factory(). Получаем
# набор форм, когда объекты одного типа, модули, будут связаны с объектом другого типа, курсами.
# Мы также передали в фабричную функцию следующие аргументы:
#   - fields – поля, которые будут добавлены для каждой формы набора;
#   - extra – количество дополнительных пустых форм модулей;
#   - can_delete. Если установить его в True, Django добавит для каждой формы модулей чекбокс, с помощью которого
#   можно отметить объект к удалению.
