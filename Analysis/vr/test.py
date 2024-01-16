import numpy as np
import pandas as pd

#from main.hands import *
#trial = Trial(trial=0,holes=1,when_was_shown='first',stage='all')
#hands = Hands(trial.trial,trial.holes, trial.when_was_shown)
#hands.ImportHands('left', 5)

#%%
from jan_24.dataset_2 import *
data_manager = ManageData()

#%%
# this loads each file individually
general = data_manager.import_general(subj=5,trial=1,holes=1,toDataFrame=True)
L_hand = data_manager.import_hands(subj=5,trial=1,holes=1,hand='left',toDataFrame=True)
R_hand = data_manager.import_hands(subj=5,trial=1,holes=1,hand='right',toDataFrame=True)
surface = data_manager.import_surface(subj=5,trial=1,holes=1,toDataFrame=True)
fluid = data_manager.import_fluid(subj=5,trial=1,holes=1,toDataFrame=True)

#%%
# index x,y,z components of column value
#general['AgentLookingAt'].apply(lambda x: x['x'])

#%%
from jan_24.dataset_2 import *
data_manager = ManageData()
data_manager.get_syllables()
data = data_manager.load_syllables('hand')

#%%
preprocessed = data_manager.preprocess(data)
#%%
preprocessed['PalmPosition'].iloc[0]

#%%
print((data.index.get_level_values('syllable') == 1))
print((data.index.get_level_values('hand') == 'Left'))


print(data.loc[1].index.get_level_values('hand'))




#%%
R_touch = [0,1,2]
frame = 4

print([f in R_touch for f in np.arange(frame-2, frame+2, 1)])
print(any([f in R_touch for f in np.arange(frame-2, frame+2, 1)]))

#%%
#data.loc[1,:,:,:,:,'Left']['Sphere2000'].apply(lambda axis: axis['x'])
data.loc[1,:,:,:,:,'Left']['PalmPosition'].apply(lambda x: x['x'])
data.loc[1,:,:,:,:,'Left']['PalmPosition'] = {'a':1}
print(data.loc[1,:,:,:,:,'Left']['PalmPosition'])


#%%
print(data.columns)
syllable_values, syllable_counts = np.unique(data.index.get_level_values('syllable'), return_counts=True)

t = np.array(data.index.get_level_values('syllable'))



#%%
preprocess = data_manager.preprocess(data)

#%%
# Specify the values and column names
position = {'x': '0', 'y': '0', 'z': '0'}
print(position.keys())

a = pd.DataFrame(columns=position.keys(), index=range(100))

#%%
np.unique(data.index.names)

#%%
from scipy.interpolate import interp1d

from sklearn import preprocessing

normalizer = preprocessing.MinMaxScaler()
normalized = normalizer.fit_transform(np.array([[1,2,3,4,5,6,7,8],
                                                [2,2,2,5,10,18,19,20],
                                                [4,4,4,2,1,1,1,2]]).T)

normalized1d = normalizer.fit_transform(np.array([1,2,3,4,5,6,7,8]).reshape(-1, 1))