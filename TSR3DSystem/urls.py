"""TSR3DSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import compare, search
from .core import insert, views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('insert/proteins/', insert.insert_into_all_proteins_table, name='insert-proteins'),
    path('insert/key-occurrences/', insert.key_occurrence, name='insert-occurrences'),
    path('insert/similarities/', insert.similarity_data, name='insert-similarities'),

    path('compare/proteinid/', compare.CompareByProteinID.as_view(), name='compare_by_pid_home'),
    path('compare/byprotienid/result/', compare.compare_by_protein_id_result, name='compare_by_pid_result'),
    path('compare/byhierarchy/', compare.CompareByHierarchy.as_view(), name="compare_by_hl_home"),
    path('compare/byhierarchy/result/', compare.compare_by_hierarchy_result, name='compare_by_hl_result'),

    path('search/proteinid/', search.SearchByProteinID.as_view(), name="search_by_pid_home"),
    path('search/proteinid/result/', search.search_by_protein_id, name='search_by_pid_result'),
    path('search/proteinid-seq/', search.SearchByProteinIDAndSeq.as_view(), name="search_by_pid_seq_home"),
    path('search/protenid-seq/seq/result/', search.search_by_protein_id_seq_step2, name='search_by_pid_seq_search_result'),
    path('search/proteinkey/(<pk>[0-9]+)/', search.SearchProteinKey.as_view(), name="search_protein_key"),

]
