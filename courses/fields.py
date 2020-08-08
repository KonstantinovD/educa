from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super(OrderField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:
            # Значение пусто.
            try:
                qs = self.model.objects.all()
                if self.for_fields:
                    # Фильтруем объекты с такими же значениями полей,
                    # перечисленных в "for_fields".
                    query = {field: getattr(model_instance, field) for field in self.for_fields}
                    qs = qs.filter(**query)
                # Получаем заказ последнего объекта.
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(OrderField, self).pre_save(model_instance, add)
#   Это класс поля OrderField. Он наследуется от PositiveIntegerField, который определен в Django. Конструктор принимает
# необязательный параметр for_fields, чтобы определить поле родительского объекта, относительно которого
# будет вычислен порядок.
#   Мы переопределили метод pre_save() класса PositiveIntegerField. Он выполняется перед тем, как Django сохранит поле
# в базу данных. В этом методе мы выполняем следующие действия:
# 1) проверяем, существует ли такое значение для объектов модели. Для того чтобы получить имя поля, по которому оно было
# определено в модели, обращаемся к атрибуту self.attname. Если значение поля равно None, рассчитываем, чему оно должно
# быть равно:
# формируем QuerySet, чтобы получить все объекты модели. Класс мо-
# дели, для которой определено текущее поле, получаем через запись
# self.model;
#   - если был задан параметр for_fields, получаем для текущего объекта значения этих полей и фильтруем QuerySet по ним.
#   Так мы получим только те объекты, которые принадлежат одному родительскому, например, все модули курса;
#   - получаем объект с максимальным значением порядкового номера из результата фильтрации с помощью записи
#   last_item = qs.latest(self.attname). Если не найдено ни одного объекта, присваиваем текущему порядковый номер 0;
#   - если объект найден, то присваиваем текущему номер, больший на единицу;
# 2) если поле заполнено пользователем, ничего не делаем.
# !ВАЖНО! Когда вы создаете собственные поля для моделей, старайтесь делать их универсальными. Избегайте явного задания
# данных или полей моделей, от которых они могут зависеть. Поля должны быть применимы не для одной модели, а для всех.




