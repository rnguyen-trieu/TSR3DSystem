import time
from operator import itemgetter

from django.db.models import Q
from django.views.generic.list import ListView
from django.template.response import TemplateResponse

from .models import Hierarchy, Comparison
from .core.views import nav_bar


class CompareByProteinID(ListView):
    model = Hierarchy
    template_name = "compare/compare_by_pid_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(nav_bar())
        return context


def compare_by_protein_id_result(request):
    start = time.clock()
    context = {}

    if request.method == "POST":
        row_val = []
        protein_compared = request.POST["list1"]
        protein_list = request.POST.getlist("list2")
        context['protein_compared'] = protein_compared

        if not protein_list:
            queryset = Hierarchy.objects.all()
            for query in queryset:
                protein_list.append(query.pk)

        # if protein_compared not in protein_list:
        #     protein_list.append(protein_compared)

        for protein in protein_list:
            queryset = Comparison.objects.filter(Q(protein_one=protein_compared) | Q(protein_two=protein_compared))

            if protein == protein_compared:
                continue

            similarity_value = queryset[0].similarity_value

            # hierarchy_result = Hierarchy.objects.get(pk=protein)

            # class_result = CLASS_DESCRIPTION.objects.get(
            #     Class=hierarchy_result.Class_id)

            # architecture_result = ARCHITECTURE_DESCRIPTION.objects.get(
            #     Architecture=hierarchy_result.Architecture_id)

            # topology_result = TOPOLOGYFOLD_DESCRIPTION.objects.get(
            #     TopologyFold=hierarchy_result.TopologyFold_id)

            # homology_result = HOMOLOGYSUPERFAMILY_DESCRIPTION.objects.get(
            # HomologySuperfamily=hierarchy_result.HomologySuperfamily_id)

            row_val.append({
                'ProtId': protein,
                'similarity': similarity_value,
                # 'class': hierarchy_result.Class_id,
                # 'class_desc': class_result.DescriptionOfClass,
                # 'archi': hierarchy_result.Architecture_id,
                # 'archi_desc': architecture_result.DescriptionOfArchitecture,
                # 'topfold': hierarchy_result.TopologyFold_id,
                # 'topfold_desc': topology_result.DescriptionOfTopologyFold,
                # 'homsup': hierarchy_result.HomologySuperfamily_id,
                # 'homsup_desc': homology_result.DescriptionOfHomologySuperfamily
            })

        context['protein_details_list'] = sorted(
            row_val, key=itemgetter('similarity'), reverse=True)
    else:
        context['no_result_found'] = True
    end = time.clock()
    context['time'] = round(end - start, 4)
    context.update(nav_bar())
    return TemplateResponse(request, 'compare/compare_by_pid_result.html', context)


class CompareByHierarchy(ListView):
    model = Hierarchy
    template_name = "compare/compare_by_hl_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(nav_bar())
        return context


def compare_by_hierarchy_result(request):
    start = time.clock()
    context = {}

    if request.method == "GET":
        context['no_result_found'] = True

    if request.method == "POST":
        row_val = []
        protein_list = []
        protein_id = request.POST["list1"]
        class_id = int(request.POST["classes"])
        architecture = int(request.POST["architectures"])
        topology = int(request.POST["topfolds"])
        homology = int(request.POST["homologies"])

        if architecture == 0 or topology == 0 or homology == 0:
            hierarchy_list = get_hierarchy_list(
                class_id, architecture, topology, homology)

            for hierarchy in hierarchy_list:
                hierarchy_result = Hierarchy.objects.filter(
                    Class=hierarchy[0],
                    Architecture_id=hierarchy[1],
                    TopologyFold_id=hierarchy[2],
                    HomologySuperfamily_id=hierarchy[3])

                for hresult in hierarchy_result:
                    protein_list.append(hresult.Protein_ID)
        else:
            hierarchy_result = Hierarchy.objects.filter(
                Class=class_id, Architecture=architecture,
                TopologyFold=topology,
                HomologySuperfamily=homology)

            for hresult in hierarchy_result:
                protein_list.append(hresult.Protein_ID)

        for protein in protein_list:
            similarity_info_queryset = SIMILARITY_INFORMATION.objects.filter(
                Protein_ID1_id=protein_id,
                Protein_ID2_id=protein)

            if not similarity_info_queryset:
                continue

            similarity_value = similarity_info_queryset[0].Similarity_Value

            hierarchy_result = Hierarchy.objects.get(Protein_ID=protein)

            class_result = CLASS_DESCRIPTION.objects.get(
                Class=hierarchy_result.Class_id)

            architecture_result = ARCHITECTURE_DESCRIPTION.objects.get(
                Architecture=hierarchy_result.Architecture_id)

            topology_result = TOPOLOGYFOLD_DESCRIPTION.objects.get(
                TopologyFold=hierarchy_result.TopologyFold_id)

            homology_result = HOMOLOGYSUPERFAMILY_DESCRIPTION.objects.get(
                HomologySuperfamily=hierarchy_result.HomologySuperfamily_id)

            row_val.append({
                'ProtId': protein,
                'similarity': similarity_value,
                'class': hierarchy_result.Class_id,
                'class_desc': class_result.DescriptionOfClass,
                'archi': hierarchy_result.Architecture_id,
                'archi_desc': architecture_result.DescriptionOfArchitecture,
                'topfold': hierarchy_result.TopologyFold_id,
                'topfold_desc': topology_result.DescriptionOfTopologyFold,
                'homsup': hierarchy_result.HomologySuperfamily_id,
                'homsup_desc': homology_result.DescriptionOfHomologySuperfamily
            })

        context['protein_compared'] = protein_id
        context['protein_details_list'] = sorted(
            row_val, key=itemgetter('similarity'), reverse=True)

    end = time.clock()
    context['time'] = round(end - start, 4)
    context.update(nav_bar())
    return TemplateResponse(request, 'compare/compare_by_hl_result.html', context)
