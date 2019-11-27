from .core import settings, background_tasks

from django import forms


def get_class_choices():
    classes = []
    for each in settings.DATABASES:
        classes.append((each, each))
    return classes


class ClassMaxDistance(forms.Form):
    max_distance = forms.IntegerField(required=True, max_value=20, min_value=6)
    protein_class = forms.ChoiceField(choices=get_class_choices(), required=True)
    email = forms.EmailField(required=True)
    # min_support = forms.FloatField(max_value=1, min_value=0.80, required=True)
    min_support = forms.FloatField(max_value=1, min_value=0.00, required=True)
    # min_confidence = forms.FloatField(max_value=1, min_value=0.80, required=True)
    min_confidence = forms.FloatField(max_value=1, min_value=0.00, required=True)

    def clean(self):
        cleaned_data = super().clean()

        background_tasks.class_filter(cleaned_data.get('email'),
                                      cleaned_data.get('protein_class'),
                                      cleaned_data.get('max_distance'),
                                      cleaned_data.get('min_support'),
                                      cleaned_data.get('min_confidence'),
                                      )