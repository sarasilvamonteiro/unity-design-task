import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import umap
import pandas as pd
from jan_24.dataset_2 import *
from sklearn.decomposition import PCA
from imblearn.under_sampling import RandomUnderSampler


data_manager = ManageData(IOS=True)

# last_update: 27 Feb 24

def draw_umap(umap_values, hand, holes='all', trial='all', n_neighbors=15, min_dist=0.1, n_components=2, lr=1, metric='euclidean',
              title='', pca_components=False, up_vs_down=False, balance=False):  # 'euclidean'

    suptitle = f'Hand: {hand.lower()} Trial: {trial} Holes: {holes}'#  (sorted by {sort_by})'
    title = f'(neigh:{n_neighbors} min-dist:{min_dist} pca:{str(pca_components).lower()}, balance:{str(balance).lower()})'
    print(suptitle)

    #umap_values = umap_values.sort_index(level='id').sort_index(level=['subject', 'level_order', 'trial'])
    #print(umap_values.index)

    fit = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric,
        learning_rate=lr)

    pca_ = PCA(n_components=pca_components)

    if trial != 'all':
        if holes == 'all':
            trial_data = umap_values.loc[:, umap_values.index.isin(data_manager.section_list, level=1), :, trial, :, :, hand]
        else:
            trial_data = umap_values.loc[:, umap_values.index.isin(data_manager.section_list, level=1), :, trial, holes, :, hand]
    else: # trial == all
        if holes == 'all':
            trial_data = umap_values.loc[:, umap_values.index.isin(data_manager.section_list, level=1), :, :, :, :, hand]
        else:
            trial_data = umap_values.loc[:, umap_values.index.isin(data_manager.section_list, level=1), :, :, holes, :, hand]


    trial_syllables = trial_data.index.get_level_values('syllable')
    trial_number = trial_data.index.get_level_values('trial')
    #print(trial_syllables)

    if balance:
        runs = RandomUnderSampler(random_state=42)
        trial_data, trial_syllables = runs.fit_resample(trial_data, trial_syllables)
        trial_data = trial_data.sort_index(level='id').sort_index(level=['subject', 'trial', 'holes', 'level_order'])
        trial_syllables = trial_data.index.get_level_values('syllable')
        #print(trial_data.index)

    labels, counts = np.unique(trial_syllables, return_counts=True)
    nr_train_samples = dict(zip(labels, counts))
    print(nr_train_samples)

    section_cmap = []
    direction = []
    up = []
    down = []
    for idx, syllable in enumerate(trial_syllables):
        if syllable[1] in ['F', 'M', 'B']:
            LCR = syllable[0]
            BMF = syllable[1]
        if syllable[1] not in ['F', 'M', 'B']:
            LCR = syllable[0:2]
            BMF = syllable[2]
        color, index = data_manager.section_cmap(LCR, BMF, length=100, return_index=True)
        section_cmap.append(color)
        direction.append(index)
        if syllable[-2:] == 'Up':
            up.append(idx)
        if syllable[-4:] == 'Down':
            down.append(idx)
    direction = np.array(direction)
    final_vector = []
    for i in range(len(trial_syllables) - 1):
        print(trial_number[i], trial_number[i+1])
        vector = direction[i + 1] - direction[i]
        if trial_number[i + 1] != trial_number[i]:
            vector = np.zeros((1, 2))[0]
        final_vector.append(vector)
    final_vector.append(np.zeros((1,2))[0])
    final_vector = np.array(final_vector)

    if pca_components != False:
        pca_vals = pca_.fit_transform(trial_data)
        u = fit.fit_transform(pca_vals)
    if not pca_components:
        u = fit.fit_transform(trial_data)

    fig = plt.figure(figsize=(10, 5))
    gs = gridspec.GridSpec(1, 2, width_ratios=[2*n_components, 2/n_components], height_ratios=[1])

    #print(len(section_cmap), len(up), len(down), len(u), len(trial_data.iloc[up+down]))
    color = ['black', 'silver']

    if n_components == 2:
        # plot UMAP
        ax1 = plt.subplot(gs[0])
        ax1.set_title(title)
        # plot up vs. down:
        if up_vs_down:
            ax1.scatter(u[:, 0][up], u[:, 1][up], c=color[0], marker=r'$\Uparrow$', s=200)
            ax1.scatter(u[:, 0][down], u[:, 1][down], c=color[1], marker=r'$\Downarrow$', s=200)
        # plot surface section:
        else:
            #ax1.scatter(u[:, 0][up], u[:, 1][up], c=[section_cmap[i] for i in up], marker=r'$\Uparrow$', s=200)
            #ax1.scatter(u[:, 0][down], u[:, 1][down], c=[section_cmap[i] for i in down], marker=r'$\Downarrow$', s=200)
            ax1.quiver(u[:,0][up], u[:,1][up], 0.002*final_vector[:,0][up], 0.002*final_vector[:,1][up],
                       pivot='tail', color=[section_cmap[i] for i in up], width=0.01)
            ax1.quiver(u[:, 0][down], u[:, 1][down], 0.001*final_vector[:, 0][down], 0.001*final_vector[:, 1][down],
                       pivot='tail', color=[section_cmap[i] for i in down], width=0.005)


        # to do: make direction only between same trial

                # plot line:
        #ax1.plot(u[:, 0],u[:, 1], linewidth=0.4, c='k')
        ax1.set_aspect('auto')
    if n_components == 3:
        ax1 = plt.subplot(gs[0], projection='3d')
        ax1.set_title(title)
        ax1.scatter(u[:, 0][up], u[:, 1][up], c=[section_cmap[i] for i in up], s=100, marker=r'$\Uparrow$')
        ax1.scatter(u[:, 0][down], u[:, 1][down], c=[section_cmap[i] for i in down], marker=r'$\Downarrow$')
        #ax1.plot(u[:, 0], u[:, 1], linewidth=0.4, c='k')
        ax1.set_aspect('auto')

    # plot 2D cmap
    ax2 = plt.subplot(gs[1])
    cmap = ax2.imshow(data_manager.cmap)
    ax2.set_aspect('equal')
    ax2.set_title('surface\n(top down view)', fontsize=12)
    ax2.set_xticks([0, 50, 100])
    ax2.set_yticks([0, 50, 100])
    ax2.set_xticklabels(['Left', 'Center', 'Right'], fontsize=9)
    ax2.set_yticklabels(['Back', 'Middle', 'Front'], fontsize=9)
    fig.suptitle(suptitle, fontsize=16)
    fig.tight_layout()
    plt.show()


def draw_umap_by_trial(umap_values, hand, holes, trial='all', n_neighbors=15, min_dist=0.1, n_components=2, lr=1, metric='euclidean',
              title=''):  # 'euclidean'

    suptitle = f'Hand: {hand.lower()} Trial: {str(trial)} Holes: {str(holes)}'#  (sorted by {sort_by})'
    title = f'(neigh:{str(n_neighbors)} min-dist:{str(min_dist)})'

    if trial == 'all':
        trials = np.arange(1,7,1)
    else:
        trials = [trial]

    runs = RandomUnderSampler(random_state=42)

    fig = plt.figure(figsize=(10, 5))
    gs = gridspec.GridSpec(1, 2, width_ratios=[2 * n_components, 2 / n_components], height_ratios=[1])

    fit = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric,
        learning_rate=lr,
        random_state=2
    )

    subj_color = ['black', 'silver'] # one color per subject

    for trial in trials:
        s = -1
        for subj in [1,2]:
            s += 1
            try:
                trial_data = umap_values.loc[:, :, subj, trial, holes, :, hand]
            except:
                continue

            if len(trial_data) <= n_neighbors+1:
                print('next', len(trial_data))
                continue

            trial_syllables = trial_data.index.get_level_values('syllable')
            section_cmap = []
            up = []
            down = []
            for idx, syllable in enumerate(trial_syllables):
                if syllable[1] in ['F', 'M', 'B']:
                    LCR = syllable[0]
                    #print(LCR)
                    BMF = syllable[1]
                    #print(BMF)
                if syllable[1] not in ['F', 'M', 'B']:
                    LCR = syllable[0:2]
                    #print(LCR)
                    BMF = syllable[2]
                    #print(BMF)

                section_cmap.append(data_manager.section_cmap(LCR, BMF, length=100))

                if syllable[-2:] == 'Up':
                    up.append(idx)
                if syllable[-4:] == 'Down':
                    down.append(idx)

            print(len(trial_data))
            print(np.min((n_neighbors, len(trial_data)-1)))
            print(trial_data)

            u = fit.fit_transform(trial_data)
            # normalize u:
            normalizer = preprocessing.MinMaxScaler()
            u = normalizer.fit_transform(u)
            print(u.shape)

            if n_components == 2:
                # plot UMAP
                ax1 = plt.subplot(gs[0])
                ax1.set_title(title)
                ax1.scatter(u[:, 0][up], u[:, 1][up], c=[section_cmap[i] for i in up], marker=r'$\Uparrow$', s=200)
                ax1.scatter(u[:, 0][down], u[:, 1][down], c=[section_cmap[i] for i in down], marker=r'$\Downarrow$', s=200)
                ax1.plot(u[:, 0],u[:, 1], linewidth=0.4, c=subj_color[s])
                ax1.set_aspect('auto')
            if n_components == 3:
                ax1 = plt.subplot(gs[0], projection='3d')
                ax1.set_title(title)
                ax1.scatter(u[:, 0][up], u[:, 1][up], c=[section_cmap[i] for i in up], s=100, marker=r'$\Uparrow$')
                ax1.scatter(u[:, 0][down], u[:, 1][down], c=[section_cmap[i] for i in down], marker=r'$\Downarrow$')
                ax1.plot(u[:, 0], u[:, 1], linewidth=0.4, c='k')
                ax1.set_aspect('auto')

    # plot 2D cmap
    ax2 = plt.subplot(gs[1])
    cmap = ax2.imshow(data_manager.cmap)
    ax2.set_aspect('equal')
    ax2.set_title('surface\n(top down view)', fontsize=12)
    ax2.set_xticks([0, 50, 100])
    ax2.set_yticks([0, 50, 100])
    ax2.set_xticklabels(['Left', 'Center', 'Right'], fontsize=9)
    ax2.set_yticklabels(['Back', 'Middle', 'Front'], fontsize=9)
    fig.suptitle(suptitle, fontsize=16)
    fig.tight_layout()
    plt.show()