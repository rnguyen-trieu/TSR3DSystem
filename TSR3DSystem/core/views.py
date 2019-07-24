from django.template.response import TemplateResponse
from .forms import InsertProteinFile


def home(request):
    ctx = nav_bar()
    return TemplateResponse(request, 'home.html', ctx)


def nav_bar():
    return {'insert_proteins_form': InsertProteinFile()}
