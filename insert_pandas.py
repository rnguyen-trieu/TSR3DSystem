import multiprocessing
import os
import pandas as pd

from joblib import Parallel, delayed, parallel_backend
from sqlalchemy import create_engine


def insert_into_all_proteins_table_pandas():
    for root, dirs, files in os.walk('C:/Users/rNguy/Documents/GitKraken/TSR3DSystem/TSR3DSystem/core/mad_triplets/'):
        for file in files:
            print(file)
            chunk_list = []
            df_chunk = pd.read_csv(root + file, sep='\t',
                                   names=['protein_key', 'aacd0', 'position0', 'aacd1', 'position1', 'aacd2',
                                          'position2',
                                          'classT1', 'theta', 'classL1', 'maxDist', 'x0', 'y0', 'z0', 'x1', 'y1', 'z1',
                                          'x2', 'y2', 'z2'], chunksize=1000000)
            for chunk in df_chunk:
                chunk_list.append(chunk[chunk.maxDist <= 20])
            df_concat = pd.concat(chunk_list)
            df_concat['protein_id'] = str(os.path.splitext(file)[0])
            # engine = create_engine('postgresql://richn:komiisawsome@tsr3dsystem.cmix.louisiana.edu:5432/tsr3d_kinase')
            engine = create_engine('postgresql://postgres:@Xsockmonkey1@localhost:5432/protein')
            df_concat.to_sql('fallproteins', engine, if_exists='append')


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
    df_concat.to_csv(file, index=False)

# for root, dirs, files in os.walk('C:/Users/rNguy/Documents/GitKraken/TSR3DSystem/TSR3DSystem/core/mad_triplets/'):
#     for file in files:
#         filter_csv(root, file)

num_cores = multiprocessing.cpu_count()

for root, dirs, files in os.walk('C:/Users/rNguy/Documents/GitKraken/TSR3DSystem/TSR3DSystem/core/mad_triplets/'):
    Parallel(n_jobs=num_cores, backend='threading')(delayed(filter_csv)(root, file) for file in files)
