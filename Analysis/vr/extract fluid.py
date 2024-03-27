import numpy as np

from jan_24.draw_umap_2 import *
data_manager = ManageData(Windows=True)
#%%

def fluid_score(holes):
    """ Score is computed by getting the percentage of fluid collected (of fluid collected """
    print(f'Extracting score for level {holes}:')
    trial_score = np.zeros((7, len(data_manager.subjects)))
    for trial in np.arange(1,8,1):
        subjects_score = np.zeros(len(data_manager.subjects))
        for s, subj in enumerate(data_manager.subjects):
            fluid = data_manager.import_fluid(subj, trial, holes, True)
            fluid.dropna(subset=['FluidInHole'], inplace=True)
            fluid_emitted = fluid['FluidEmitted'].values.astype(int)

            if holes == 1:
                total_fluid = [x + y + z for x, y, z in zip(fluid['FluidInHole'].apply(lambda x: int(x['x'])),
                                                            fluid['FluidInHole'].apply(lambda y: int(y['y'])),
                                                            fluid['FluidInHole'].apply(lambda z: int(z['z'])))]
            if holes == 2:
                total_fluid = [x + y + z if (x > 0 and y > 0) else 0 for x, y, z
                               in zip(fluid['FluidInHole'].apply(lambda x: int(x['x'])),
                                      fluid['FluidInHole'].apply(lambda y: int(y['y'])),
                                      fluid['FluidInHole'].apply(lambda z: int(z['z'])))]
            # to do: get cummulative score
            subjects_score[s] = total_fluid[-1]/fluid_emitted[-1]
        trial_score[trial-1] = subjects_score
    print('Done.')
    return trial_score


#%%
score_1 = fluid_score(1)
score_2 = fluid_score(2)
#%%
best_subject_trial_1 = np.unravel_index(np.argmax(score_1), score_1.shape)
best_subject_trial_2 = np.unravel_index(np.argmax(score_2), score_2.shape)
#%%
subj_score_sum_1 = np.sum(score_1, axis=1)
best_trial_1 = np.argmax(subj_score_sum_1)
subj_score_sum_2 = np.sum(score_2, axis=1)
best_trial_2 = np.argmax(subj_score_sum_2)
