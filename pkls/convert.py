import numpy as np
import pickle
import pandas as pd

backward_dfs = []

for duplication_round in range(3):
    for shift in range(2):
        df_of_split = pickle.load(open('BTE_shift_{}.p'.format(shift), 'rb'), encoding = 'latin1')
        df_of_split['shift'] = np.array(df_of_split['shift']) + duplication_round * 2
        backward_dfs.append(df_of_split)
    
backward_df = pd.concat(backward_dfs)

forward_dfs = []

for duplication_round in range(3):
    for shift in range(2):
        df_of_split = pickle.load(open('FTE_shift_{}.p'.format(shift), 'rb'), encoding = 'latin1')
        df_of_split['shift'] = np.array(df_of_split['shift']) + duplication_round * 2
        forward_dfs.append(df_of_split)
    
forward_df = pd.concat(forward_dfs)

pickle.dump((forward_df, backward_df), open('FTE_BTE_tuple.p', 'wb'))
