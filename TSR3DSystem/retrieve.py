import time
from collections import Counter
from itertools import combinations

from django.db.models import Q
from django.db.models.aggregates import Count
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.template.response import TemplateResponse

from .core import settings
from .core.views import nav_bar
from .models import AllProteins, Hierarchy


class RetrieveProteinByID(ListView):
    model = Hierarchy
    template_name = 'retrieve/retrieve_protein.html'

def retrieve_by_protein_id(request):
    """
    Input: A selected protein id & max distance
    Output: Full protein according to max distance
    """
    start = time.clock()
    context = {}
    protein_selected = request.POST.get("protein")
    max_distance = request.POST.get("max_distance")

    protein = Hierarchy.objects.get(pk=protein_selected)
    full_protein = protein.details.filter(maxDist__lte=int(max_distance))

    context['protein'] = protein_selected
    context['max_distance'] = max_distance
    context['full_protein'] = full_protein
    context['time'] = round(time.clock() - start, 4)
    context.update(nav_bar())
    return TemplateResponse(request, 'retrieve/retrieve_protein_results.html', context)