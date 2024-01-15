from dataset import *
import umap
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
#%%
ManageData()
#ManageData().generate_syllables()
#%%
# load csv
hands_syllables = ManageData().load_syllables('hands')
surface_syllables = ManageData().load_syllables('surface')
preprocess_hands = ManageData().preprocess(hands_syllables)
umap_values = ManageData().extract_values(preprocess_hands, as_array=False)
#%%
#plt.figure(figsize=(4,2))
#palm_3 = plt.plot(preprocess_hands['PalmPosition'].iloc[3][['x','y', 'z']])
#plt.show()
#%%
def draw_umap(hand, holes, trial='all', n_neighbors=15, min_dist=0.1, n_components=2, lr=1, metric='euclidean',
              title=''):  # 'euclidean'

    sort_by = 'time_interval'
    data = umap_values.sort_values(by=sort_by)
    # get syllables in data (sorted by^'____________')
    data_syllables = data.index.get_level_values('syllable')
    print(data_syllables)
    # get int and str labels for each unique syllable
    int_labels , str_labels = pd.factorize(data_syllables.unique())
    # create a dictionary between them
    labels_dict =  dict(zip(str_labels, int_labels))
    print(labels_dict)

    suptitle = f'Hand: {hand.lower()} Trial: {str(trial)} Holes: {str(holes)}'#  (sorted by {sort_by})'
    title = f'(neigh:{str(n)} min-dist:{str(d)})'

    fit = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric,
        learning_rate=lr
    )

    if trial != 'all':
        trial_data = data.loc[:, trial, holes, :, hand, :]
    else:
        trial_data = data.loc[:, :, holes, :, hand, :]

    # get from the label dictionary the int_label for the syllables in this trial
    trial_labels = [labels_dict[key] for key in trial_data.index.get_level_values('syllable')]

    trial_syllables = trial_data.index.get_level_values('syllable')
    section_cmap = []
    up = []
    down = []
    for idx, syllable in enumerate(trial_syllables):
        if syllable[1] in ['F', 'M', 'B']:
            LCR = syllable[0]
            BMF = syllable[1]
        if syllable[1] not in ['F', 'M', 'B']:
            LCR = syllable[0:2]
            BMF = syllable[2]
        section_cmap.append(ManageData().section_cmap(LCR, BMF))

        if syllable[-2:] == 'Up':
            up.append(idx)
        if syllable[-4:] == 'Down':
            down.append(idx)


    u = fit.fit_transform(trial_data.drop(['time_interval', 'labels'], axis=1))

    fig = plt.figure(figsize=(6, 3))
    gs = gridspec.GridSpec(1, 2, width_ratios=[2*n_components, 2/n_components], height_ratios=[1])

    if n_components == 2:
        # plot UMAP
        ax1 = plt.subplot(gs[0])
        ax1.set_title(title)
        ax1.scatter(u[:, 0][up], u[:, 1][up], c=[section_cmap[i] for i in up], marker=r'$\uparrow$')
        ax1.scatter(u[:, 0][down], u[:, 1][down], c=[section_cmap[i] for i in down], marker=r'$\downarrow$')
        ax1.plot(u[:, 0],u[:, 1], linewidth=0.2, c='k')
        ax1.set_aspect('auto')
    if n_components == 3:
        ax1 = ax1 = plt.subplot(gs[0], projection='3d')
        ax1.set_title(title)
        ax1.scatter(u[:, 0][up], u[:, 1][up], c=[section_cmap[i] for i in up], s=100, marker=r'$\uparrow$')
        ax1.scatter(u[:, 0][down], u[:, 1][down], c=[section_cmap[i] for i in down], marker=r'$\downarrow$')
        ax1.plot(u[:, 0], u[:, 1], linewidth=0.2, c='k')
        ax1.set_aspect('auto')

    # plot 2D cmap
    ax2 = plt.subplot(gs[1])
    cmap = ax2.imshow(ManageData().cmap)
    ax2.set_aspect('equal')
    ax2.set_title('surface\n(top down view)', fontsize=9)
    ax2.set_xticks([0, 50, 100])
    ax2.set_yticks([0, 50, 100])
    ax2.set_xticklabels(['Left', 'Center', 'Right'], fontsize=7)
    ax2.set_yticklabels(['Back', 'Middle', 'Front'], fontsize=7)
    fig.suptitle(suptitle, fontsize=14)
    fig.tight_layout()
    plt.show()


#%%
n = 5
d = 0.1
draw_umap(n_components=3,n_neighbors=n, min_dist=d, hand='Right', holes=1)
draw_umap(n_components=3,n_neighbors=n, min_dist=d, hand='Right', holes=2)
draw_umap(n_components=3,n_neighbors=n, min_dist=d, hand='Left', holes=1)
draw_umap(n_components=3,n_neighbors=n, min_dist=d, hand='Left', holes=2)


#%%


#%%













def draw_umap_backup(hand, holes, trial='all', n_neighbors=15, min_dist=0.1, n_components=2, lr=1, metric='euclidean',
              title=''):  # 'euclidean'

    sort_by = 'syllable'
    data = umap_values.sort_values(by=sort_by)
    # get syllables in data (sorted by^'____________')
    data_syllables = data.index.get_level_values('syllable')
    # get int and str labels for each unique syllable
    int_labels , str_labels = pd.factorize(data_syllables.unique())
    # create a dictionary between them
    labels_dict =  dict(zip(str_labels, int_labels))
    print(labels_dict)

    suptitle = 'sorted by ' + sort_by
    title = f'Trial: {str(trial)} Holes: {str(holes)} (neigh:{str(n)} min-dist:{str(d)})'

    fit = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric,
        learning_rate=lr
    )

    if trial != 'all':
        trial_data = data.loc[:, trial, holes, :, hand, :]
    else:
        trial_data = data.loc[:, :, holes, :, hand, :]

    # get from the label dictionary the int_label for the syllables in this trial
    trial_labels = [labels_dict[key] for key in trial_data.index.get_level_values('syllable')]

    u = fit.fit_transform(trial_data.drop(['time_interval', 'labels'], axis=1))

    fig = plt.figure(figsize=(6, 3))
    if n_components == 1:
        ax = fig.add_subplot(111)
        ax.set_title(title)
        scatter = ax.scatter(u[:, 0], range(len(u)))
        cbar = plt.colorbar(scatter, ticks=np.arange(0, len(str_labels), 1))
        cbar.ax.set_yticklabels(str_labels)
    if n_components == 2:
        ax = fig.add_subplot(111)
        ax.set_title(title)
        scatter = ax.scatter(u[:, 0], u[:, 1], c=trial_labels, vmin=0, vmax=len(str_labels) - 1)
        cbar = plt.colorbar(scatter, ticks=np.arange(0, len(str_labels), 1))
        cbar.ax.set_yticklabels(str_labels)
    if n_components == 3:
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title(title)
        scatter = ax.scatter(u[:, 0], u[:, 1], u[:, 2], c=trial_labels, s=100, vmin=0, vmax=len(str_labels) - 1)
        cbar = plt.colorbar(scatter, ticks=np.arange(0, len(str_labels), 1))
        cbar.ax.set_yticklabels(str_labels)
    #plt.title(title, fontsize=15)
    fig.suptitle(suptitle, fontsize=14)
    fig.tight_layout()
    plt.show()