import multiprocessing
import os
import pandas as pd

from joblib import Parallel, delayed, parallel_backend
from sqlalchemy import create_engine

engine = create_engine('postgresql+psycopg2://richn:komiisawsome@tsr3dsystem.cmix.louisiana.edu:5432/tsr3d_kinase')

def insert_into_all_proteins_table_pandas(root, file):
        print(file)
        chunk_list = []
        df_chunk = pd.read_csv(root + file, chunksize=1000000)
        for chunk in df_chunk:
            chunk_list.append(chunk)
        df_concat = pd.concat(chunk_list)        
        #engine = create_engine('postgresql+psycopg2://richn:komiisawsome@tsrtsr3dsystem.cmix.louisiana.edu:5432/tsr3d_kinase')
        df_concat.to_sql('TSR3DSystem_allproteins', engine,
                if_exists='append', index=False)
        print(file,' - added')


def filter_csv(root, file):
    print(file)
    chunk_list = []
    df_chunk = pd.read_csv(root + file, sep='\t',
                           names=['protein_key', 'aacd0', 'position0', 'aacd1', 'position1', 'aacd2', 'position2',
                                  'classT1', 'theta', 'classL1', 'maxDist', 'x0', 'y0', 'z0', 'x1', 'y1', 'z1',
                                  'x2', 'y2', 'z2'], chunksize=1000000)
    for chunk in df_chunk:
        chunk_list.append(chunk[chunk.maxDist <= 20])
    df_concat = pd.concat(chunk_list)
    df_concat['protein_id_id'] = str(os.path.splitext(file)[0])
    df_concat.to_csv('/mnt/space/tsr3duser/csv/Protease/'+file, index=False)



num_cores = multiprocessing.cpu_count()

for root, dirs, files in os.walk('/mnt/space/tsr3duser/csv/Kinase/'):
    Parallel(n_jobs=num_cores,
            backend='threading')(delayed(insert_into_all_proteins_table_pandas)(root,
                file) for file in files)
print('Finished inserting into Database - Kinase')



### THIS IS FOR FILTERING TO CSV
#for root, dirs, files in os.walk('/mnt/space/tsr3duser/Protease/'):
#    Parallel(n_jobs=num_cores,
#       backend='threading')(delayed(filter_csv)(root, file) for file in files)

#print('Finished Protease')
