from django import forms

from ..models import AllProteins, Hierarchy

class InsertProteinFile(forms.ModelForm):
    protein_file = forms.FileField(widget=forms.FileInput(attrs={'multiple': True, 'class': 'custom-file-input'}))

    class Meta:
        model = AllProteins
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        try:
            protein_ID = Hierarchy.objects.get(protein_id=cleaned_data['protein_file']._name.split('.')[0])
            if protein_ID:
                raise forms.ValidationError(
                    "This Protein is already in the database!"
                )
        except:
            pass
        return

    def save(self):
        protein_ID = Hierarchy.objects.create(protein_id=self.cleaned_data['protein_file']._name.split('.')[0])
        for line in self.cleaned_data['protein_file']:
        #     if counter == 5000:
        #         break
            line = line.decode().split('\t')
            protein = AllProteins(protein_key=int(line[0]), aacd0=str(line[1]), position0=int(line[2]),
                                  aacd1=str(line[3]), position1=int(line[4]), aacd2=str(line[5]),
                                  position2=int(line[6]), classT1=int(line[7]), theta=float(line[8]),
                                  classL1=int(line[9]), maxDist=float(line[10]), x0=float(line[11]),
                                  y0=float(line[12]), z0=float(line[13]), x1=float(line[14]),
                                  y1=float(line[15]), z1=float(line[16]), x2=float(line[17]),
                                  y2=float(line[18]), z2=float(line[19]))
            protein.protein_id = protein_ID
            protein.save()
