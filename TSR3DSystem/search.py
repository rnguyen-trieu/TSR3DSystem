import time
from collections import Counter
from itertools import combinations

from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.template.response import TemplateResponse

from .core import settings
from .core.views import nav_bar
from .models import AllProteins, Hierarchy


class SearchByProteinID(ListView):
    model = Hierarchy
    template_name = 'search/search_by_pid_home.html'


def search_by_protein_id(request):
    """
    Input: A set of protein ids
    Output: Common keys, by clicking on each keys, displays
    list of all protein_ids having it and other details too
    """
    start = time.clock()
    context = {}
    user_protein_list = request.POST.getlist("list3")

    if not user_protein_list:
        user_protein_list = ['1AD6', '1BYG']

    context['protein_list'] = user_protein_list

    query = """SELECT keys.protein_key AS id, COUNT(keys.protein_key) AS key_count FROM 
               (SELECT DISTINCT ON ("{0}_allproteins"."protein_key", "{0}_allproteins"."protein_id_id")
               "{0}_allproteins"."protein_key" FROM "{0}_allproteins" WHERE "{0}_allproteins"."protein_id_id" 
               IN {1} ) AS keys GROUP BY keys.protein_key HAVING COUNT(keys.protein_key) >= {2}""".format(
        settings.APP_MODEL_NAME,
        str(tuple(user_protein_list)),
        len(user_protein_list),
    )
    protein_key_queryset = AllProteins.objects.raw(query)
    """
       Distinct with specific columns for Django's ORM does not work with annotate
       Changed to raw SQL, Django forces us to have an id column,
       so a workaround is renaming the protein key column as id
    """
    protein_key_list = [each.id for each in protein_key_queryset]

    proteins = user_protein_list

    if len(protein_key_list) is 0:
        sub_query = """ SELECT protein.protein_id_id FROM (SELECT DISTINCT ON ("{0}_allproteins"."protein_key", 
                        "{0}_allproteins"."protein_id_id") "{0}_allproteins"."protein_id_id",
                        "{0}_allproteins"."protein_key" FROM "{0}_allproteins" WHERE 
                        "{0}_allproteins"."protein_key" IN {1}) AS protein GROUP BY protein.protein_id_id 
                        HAVING COUNT(protein.protein_id_id) >= {2}; """.format(
            settings.APP_MODEL_NAME,
            str(tuple(protein_key_list)),
            len(protein_key_list),
        )

        similar_proteins = AllProteins.objects.raw(sub_query)
        proteins = proteins.append([each.id for each in similar_proteins])

    context['common_keys'] = protein_key_list
    context['proteins'] = proteins
    context['time'] = round(time.clock() - start, 4)
    context.update(nav_bar())
    return TemplateResponse(request, 'search/search_by_pid_result.html', context)


class SearchProteinKey(TemplateView):
    template_name = "search/search_by_key_result.html"

    def get_context_data(self, **kwargs):
        context = super(SearchProteinKey, self).get_context_data(**kwargs)
        key = int(self.kwargs['pk'])
        context['key'] = key
        context['proteins'] = AllProteins.objects.filter(Protein_Key=key)
        context.update(nav_bar())
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
        context.update(nav_bar())
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
    context.update(nav_bar())
    return TemplateResponse(request, 'search/search_by_pid_seq_search_result.html', context)
