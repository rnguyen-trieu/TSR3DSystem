from .core import settings

from django import forms


def get_class_choices():
    classes = []
    for each in settings.DATABASES:
        classes.append((each, each))
    return classes


class ClassMaxDistance(forms.Form):
    max_distance = forms.IntegerField(required=True, max_value=20, min_value=6)
    classes = forms.ChoiceField(choices=get_class_choices(), required=True)
    email = forms.EmailField(required=True)
    min_support = forms.FloatField(required=True)
