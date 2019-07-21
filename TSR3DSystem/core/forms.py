from django import forms

from ..models import AllProteins


class InsertProteinFile(forms.ModelForm):
    protein_file = forms.FileField(widget=forms.FileInput)

    class Meta:
        model = AllProteins
        fields = []
