import time
from collections import Counter
from itertools import combinations

from django.db.models import Q
from django.db.models.aggregates import Count
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.template.response import TemplateResponse

from .models import AllProteins, Hierarchy


def home(request):
    ctx = {}
    return TemplateResponse(request, 'home.html', ctx)


class SearchByProteinID(ListView):
    model = Hierarchy
    template_name = 'search/search_by_pid_home.html'


def search_by_protein_id(request):
    """
    Input: A set of protein ids
    Output: Commom keys, by clicking on each keys, displays
    list of all protein_ids having it and other details too
    """
    start = time.clock()
    context = {}
    user_protein_list = request.POST.getlist("list3")

    if not user_protein_list and "small_table" in request.POST:
        user_protein_list = ['1a06', '1muo']

    context['protein_list'] = user_protein_list
    temp = Hierarchy.objects.filter(pk__in=user_protein_list).prefetch_related('details')
    protein_key_queryset = AllProteins.objects.filter(
        protein_id__in=user_protein_list) \
        .distinct() \
        .values('protein_key') \
        .annotate(key_count=Count('protein_key')) \
        .filter(key_count__gte=len(user_protein_list)) \
        .order_by('protein_key')
    # distinct?? what for?
    # this filter does not account for it not being in a protein but that it is more than 4 times

    protein_key_list = list(protein_key_queryset.values_list('protein_key', flat=True))

    sub_query = AllProteins.objects.filter(protein_key__in=protein_key_list) \
        .distinct().values_list('protein_id', 'protein_key')

    cnt = Counter(elem[0] for elem in sub_query)

    pro_list = [y for x, y in cnt.items() if y >= len(protein_key_list)]
    # need to fix this line
    proteins = []

    if protein_key_list and len(pro_list) < len(user_protein_list):
        proteins = user_protein_list
    else:
        for i in range(len(pro_list)):
            proteins.append(pro_list[i][0])
        print(pro_list)
    context['common_keys'] = protein_key_list
    context['proteins'] = proteins
    end = time.clock()
    context['time'] = round(end - start, 4)

    return TemplateResponse(request, 'search/search_by_pid_result.html', context)


class SearchProteinKey(TemplateView):
    template_name = "search/search_by_key_result.html"

    def get_context_data(self, **kwargs):
        context = super(SearchProteinKey, self).get_context_data(**kwargs)
        key = int(self.kwargs['pk'])
        context['key'] = key
        context['proteins'] = AllProteins.objects.filter(Protein_Key=key)
        return context


class SearchByProteinIDAndSeq(TemplateView):
    template_name = "search/search_by_pid_seq_home.html"

    def get_context_data(self, **kwargs):
        context = super(SearchByProteinIDAndSeq, self).get_context_data(**kwargs)
        protein_queryset = Hierarchy.objects.all().values('protein_id')
        protein_list = []
        for pid_dict in protein_queryset:
            for key, value in pid_dict.items():
                protein_list.append(value)

        all_seq_list = []
        for protein in protein_list:
            protein_seq_list = []
            seq_id_queryset = POSITION_INFORMATION.objects.filter(
                Q(Protein_ID=protein)) \
                .values('Seq_ID')
            for seq_dict in seq_id_queryset:
                for key, value in seq_dict.items():
                    protein_seq_list.append(int(value))
            all_seq_list.append(protein_seq_list)

        print(protein_list)
        print(all_seq_list)
        context['proteins'] = protein_list
        context['seq_id_list'] = all_seq_list
        return context


def search_by_protein_id_seq_step2(request):
    start = time.clock()
    context = {}
    if request.method == 'POST':
        protein_key_list = []
        pid = request.POST.get('pid')
        seq_list = request.POST.getlist("seq_list")
        pos_list = list(combinations(seq_list, 3))
        pid_rows = AllProteins.objects.filter(Protein_ID_id=pid)

        key_list = []
        for positions in pos_list:
            protein_keys = pid_rows.filter(
                Q(position0__in=list(positions))
                & Q(position1__in=list(positions))
                & Q(position2__in=list(positions))) \
                .distinct() \
                .values('Protein_Key')

            for key in protein_keys:
                key_list.append(key['Protein_Key'])

        protein_key_list = set(key_list)

        sub_query = []
        for key in protein_key_list:
            row_val = AllProteins.objects.filter(
                Protein_Key=str(key)) \
                .distinct() \
                .values('Protein_ID_id') \
                .order_by('Protein_ID_id')
            sub_query.append(row_val)

        sub_query_list = []
        for queryset in sub_query:
            for l in queryset:
                sub_query_list.append(str(l.get('Protein_ID_id')))

        d = {}
        cnt = Counter(elem for elem in sub_query_list)
        for key, value in cnt.items():
            d[key] = value

        pro_list = filter(lambda x: x[1] >= len(protein_key_list), d.items())

        proteins = []
        for i in range(len(pro_list)):
            proteins.append(pro_list[i][0])

        context['pid'] = pid
        context['seq_list'] = seq_list
        context['common_keys'] = protein_key_list
        context['proteins'] = proteins
        context['protein_keys_list'] = protein_key_list
    end = time.clock()
    context['time'] = round(end - start, 4)
    return TemplateResponse(request, 'search/search_by_pid_seq_search_result.html', context)
