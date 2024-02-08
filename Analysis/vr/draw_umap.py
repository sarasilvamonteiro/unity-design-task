import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import umap
from dataset import *


def draw_umap(umap_values, hand, holes, trial='all', n_neighbors=15, min_dist=0.1, n_components=2, lr=1, metric='euclidean',
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
    title = f'(neigh:{str(n_neighbors)} min-dist:{str(min_dist)})'

    fit = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric,
        learning_rate=lr)

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
            print(LCR)
            BMF = syllable[1]
            print(BMF)
        if syllable[1] not in ['F', 'M', 'B']:
            LCR = syllable[0:2]
            print(LCR)
            BMF = syllable[2]
            print(BMF)

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



def draw_umap_by_trial(umap_values, hand, holes, trial='all', n_neighbors=15, min_dist=0.1, n_components=2, lr=1, metric='euclidean',
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
    title = f'(neigh:{str(n_neighbors)} min-dist:{str(min_dist)})'

    if trial == 'all':
        trials = range(7)
    else:
        trials = [trial]

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

    subj_color = ['black', 'silver']

    for trial in trials:
        s = -1
        for subj in [12,14]:
            s += 1
            try:
                trial_data = data.loc[subj, trial, holes, :, hand, :]
            except:
                continue

            if len(trial_data) <= n_neighbors+1:
                print('next', len(trial_data))
                continue

            # get from the label dictionary the int_label for the syllables in this trial
            trial_labels = [labels_dict[key] for key in trial_data.index.get_level_values('syllable')]

            trial_syllables = trial_data.index.get_level_values('syllable')
            section_cmap = []
            up = []
            down = []
            for idx, syllable in enumerate(trial_syllables):
                if syllable[1] in ['F', 'M', 'B']:
                    LCR = syllable[0]
                    print(LCR)
                    BMF = syllable[1]
                    print(BMF)
                if syllable[1] not in ['F', 'M', 'B']:
                    LCR = syllable[0:2]
                    print(LCR)
                    BMF = syllable[2]
                    print(BMF)

                section_cmap.append(data_manager.section_cmap(LCR, BMF))

                if syllable[-2:] == 'Up':
                    up.append(idx)
                if syllable[-4:] == 'Down':
                    down.append(idx)

            print(len(trial_data))
            print(np.min((n_neighbors, len(trial_data)-1)))


            u = fit.fit_transform(trial_data.drop(['time_interval', 'labels'], axis=1))
            # normalize u:
            normalizer = preprocessing.MinMaxScaler()
            u = normalizer.fit_transform(u)

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
