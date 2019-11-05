import os

from django.shortcuts import redirect
from django.template.response import TemplateResponse

from TSR3DSystem.models import AllProteins, Hierarchy, Comparison
from .forms import InsertProteinFile
from .views import nav_bar

def insert_protein_files(request):
    if request.method == 'POST':
        insert_proteins_form = InsertProteinFile(request.POST, request.FILES)
        if insert_proteins_form.is_valid():
            insert_proteins_form.save()
    else:
        ctx = nav_bar()
        return redirect('home', ctx)


def insert_into_all_proteins_table(request):
    # Hierarchy.objects.get(pk='1GZK').delete()
    for root, dirs, files in os.walk('C:/Users/rNguy/PycharmProjects/TSR3DSystem/TSR3DSystem/core/mad_triplets/'):
        for file in files:
            print(file)
            f = open(root + file, 'r')
            protein_ID, _ = Hierarchy.objects.get_or_create(protein_id=str(os.path.splitext(file)[0]))
            for line in f:
                line = line.split('\t')
                max_dist = float(line[10])
                if max_dist <= 6:
                    protein = AllProteins(protein_key=int(line[0]), aacd0=str(line[1]), position0=int(line[2]),
                                          aacd1=str(line[3]), position1=int(line[4]), aacd2=str(line[5]),
                                          position2=int(line[6]), classT1=int(line[7]), theta=float(line[8]),
                                          classL1=int(line[9]), maxDist=max_dist, x0=float(line[11]),
                                          y0=float(line[12]), z0=float(line[13]), x1=float(line[14]),
                                          y1=float(line[15]), z1=float(line[16]), x2=float(line[17]),
                                          y2=float(line[18]), z2=float(line[19]))
                    protein.protein_id = protein_ID
                    protein.save()


def insert_into_all_proteins_table_pandas(request):
    import pandas as pd
    from sqlalchemy import create_engine
    engine = create_engine('postgresql://richn:komiisawsome@tsr3dsystem.cmix.louisiana.edu:5432/tsr3d_kinase')

    for root, dirs, files in os.walk('/mnt/space/tsr3duser/Kinase'):
        for file in files:
            print(file)
            f = open(root + file, 'r')
            protein_ID, _ = Hierarchy.objects.get_or_create(protein_id=str(os.path.splitext(file)[0]))

    for root, dirs, files in os.walk('/mnt/space/tsr3duser/Kinase'):
        for file in files:
            print(file)
            chunk_list = []
            df_chunk = pd.read_csv(root + file, sep='\t', names=['protein_key', 'aacd0', 'position0', 'aacd1', 'position1', 'aacd2', 'position2',
                                       'classT1', 'theta', 'classL1', 'maxDist', 'x0', 'y0', 'z0', 'x1', 'y1', 'z1',
                                       'x2', 'y2', 'z2'], chunksize=1000000)
            for chunk in df_chunk:
                chunk_list.append(chunk[chunk.maxDist <= 20])
            df_concat = pd.concat(chunk_list)
            df_concat['protein_id'] = str(os.path.splitext(file)[0])
            df_concat.to_sql('tsr3dsystem_allproteins', engine, if_exists='append')


def similarity_data(request):
    f = open(
        "C:/Users/rNguy/Documents/GitKraken/TSR3DSystem/TSR3DSystem/core/other/JaccardSimilarity_134Kinase_29_35_labelled.csv",
        "r")
    first_line = f.readline()
    proteins = first_line.split('\t')
    proteins.pop()
    for position, each in enumerate(proteins):
        print(each)
        if position != 0:
            proteins[position] = Hierarchy.objects.get(protein_id=each[0:4])
    category = 1
    for line in f:
        data = line.split('\t')
        for position, each in enumerate(data):
            if position != 0:
                if each == '100.0':
                    break
                protein = Comparison(protein_one=proteins[category])
                protein.protein_two = proteins[position]
                protein.similarity_value = float(each)
                protein.save()
        category += 1


def key_occurrence(request):
    hierarchy = Hierarchy.objects.all()
    for each in hierarchy:
        hierarchy_proteins = each.details.all()
        for protein in hierarchy_proteins:
            same_keys = hierarchy_proteins.filter(protein_key=protein.protein_key)
            occurences = len(same_keys)
            for same_key_protein in same_keys:
                same_key_protein.key_occurrence = occurences
                same_key_protein.save()
            print(protein.protein_key, occurences)
