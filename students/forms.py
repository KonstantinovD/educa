from django import forms
from courses.models import Course


class CourseEnrollForm(forms.Form):
    # Мы будем использовать эту форму при записи студентов на курсы. В поле course содержится идентификатор курса,
    # на который происходит запись. Мы определили его тип как ModelChoiceField и указали виджет HiddenInput,
    # т.к. не хотим, чтобы пользователь видел поле. Эта форма будет использоваться в обработчике CourseDetailView.
    course = forms.ModelChoiceField(queryset=Course.objects.all(),
                                    widget=forms.HiddenInput)
