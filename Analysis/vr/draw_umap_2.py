import matplotlib.gridspec as gridspec
import matplotlib
import numpy as np

matplotlib.use('module://backend_interagg')
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import umap
from jan_24.dataset_2 import *
from sklearn.decomposition import PCA
from imblearn.under_sampling import RandomUnderSampler
from sklearn.metrics.pairwise import cosine_similarity

data_manager = ManageData(IOS=True)

# last_update: 19 Mar 24

def draw_umap(umap_values, hand, holes='all', trial='all', n_neighbors=15, min_dist=0.1, n_components=2, lr=1,
              metric='euclidean', vf_min_dist=1, pca_components=False, up_vs_down=False, balance=False):  # 'euclidean'

    suptitle = f'Hand: {hand.lower()} Trial: {trial} Holes: {holes}'#  (sorted by {sort_by})'
    title = (f'(neigh:{n_neighbors} min-dist:{min_dist} vf-min-dist:{vf_min_dist} pca:{str(pca_components).lower()}, '
             f'balance:{str(balance).lower()})')
    print(suptitle)

    #####################################
    #####################################
    umap_ = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        n_components=n_components,
        metric=metric,
        learning_rate=lr)
    pca_ = PCA(n_components=pca_components)
    #####################################
    #####################################
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
    trial_subjects = np.unique(trial_data.index.get_level_values('subject'))

    #####################################
    # Average over all subjects by trial:
    # list for all subjects trajectory indices


    trial = 7
    trajectory_test = [] # [[subj1_trial1], [subj2_trial1], ...]
    for subj in trial_subjects[:2]: # get all subjects
        # individual subject list for trial 1 trajectory indices (for now)
        subj_trajectory = []
        # Testing with just the first trial:
        [[subj_trajectory.append(this_syllable) for this_syllable in range(len(trial_data)) if
          (trial_data.values[this_syllable] == trial_data.loc[:,:,subj,trial,:,:,hand].values[that_syllable]).all()]
        for that_syllable in range(len(trial_data.loc[:,:,subj,trial,:,:,hand]))]
        trajectory_test.append(subj_trajectory)
    print(trajectory_test)


    #####################################
    # Balance data to have the same nr. of each syllable:
    if balance:
        runs = RandomUnderSampler(random_state=42)
        trial_data, _ = runs.fit_resample(trial_data, trial_syllables) # out: trial data, trial syllables
        # We need to sort this way so that it is organized in the same order as original dataset
        trial_data = trial_data.sort_index(level='id').sort_index(level=['subject', 'trial', 'holes', 'level_order'])
        trial_syllables = trial_data.index.get_level_values('syllable')
    labels, counts = np.unique(trial_syllables, return_counts=True)
    nr_train_samples = dict(zip(labels, counts))
    print(nr_train_samples)
    #####################################
    ##### Fit data to PCA and UMAP: #####
    #####################################
    print("Fitting data...")
    if pca_components != False:
        pca_vals = pca_.fit_transform(trial_data)
        u = umap_.fit_transform(pca_vals)
    if not pca_components:
        u = umap_.fit_transform(trial_data)
    print(u.shape)
    print(trial_data.shape)
    plt.scatter(pca_vals[:,0], pca_vals[:,1])
    plt.show()
    #####################################
    ######### Get section info ##########
    #####################################
    section_cmap = [] # current position color
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
        if syllable[-2:] == 'Up':
            up.append(idx)
        if syllable[-4:] == 'Down':
            down.append(idx)
    #####################################
    ######## Get direction info #########
    #####################################
    # Position, direction (vector field), and color computations:
    final_vector = []   # direction
    next_color = []     # next position color (direction)
    # Iterate over all syllables:
    for i in range(len(trial_syllables) - 1):
        # Vector pointing at next umap value (next syllable)
        vector = (u[i + 1] - u[i]) / np.linalg.norm((u[i + 1] - u[i]))
        # Next syllable's surface section color (where we're going)
        color = section_cmap[i+1]
        # Check if next trial is different from current
        if trial_number[i + 1] != trial_number[i]:
            # Add zero vector to last syllable of current trial
            vector = np.zeros((1, 2))[0]
            color = section_cmap[i]
        final_vector.append(vector)
        next_color.append(color)
    final_vector.append(np.zeros((1, 2))[0]) # Append zero to last syllable of last trial
    next_color.append(section_cmap[i])       # Append current color to last syllable of last trial
    final_vector = np.array(final_vector) * 0.7 # Scale final vector
    next_color = np.array(next_color)
    #####################################
    # Define color map for vector field
    cmap = LinearSegmentedColormap.from_list("white_black", [(1, 1, 1), (0, 0, 0)], N=100)
    # Compute cosine similarity matrix between direction vector
    cos_sim_matrix = (cosine_similarity(final_vector) + 1) / 2
    #####################################
    ######## Get closeby pos/dir ########
    #####################################
    # Compute distance matrix
    distances = np.linalg.norm(u[:, np.newaxis] - u, axis=2)
    # Set a threshold for "closeby" positions
    threshold = vf_min_dist
    # Find closeby positions
    closeby_indices = np.where(distances < threshold)
    print(closeby_indices)
    # Compute average directions for closeby positions
    average_directions = []
    average_positions = []
    color_position = []     # average color position (where avg direction starts from)
    color_direction = []    # average color direction (vector field)
    color_main_vf = []      # cmap of avg direction similarity to all directions

    for i in range(len(u)):
        # Get closeby indices for current syllable (i)
        closeby_indices_for_position = closeby_indices[1][closeby_indices[0] == i]
        # Average position/direction considering all syllables (all umap values)
        if len(closeby_indices_for_position) > 0:
            average_dir = np.mean(final_vector[closeby_indices_for_position], axis=0)
            average_directions.append(average_dir)
            average_pos = np.mean(u[closeby_indices_for_position], axis=0)
            average_positions.append(average_pos)
            # Compute average similarity between all points involved to get the corresponding color
            alpha = np.mean(np.unique([cos_sim_matrix[i, closeby_indices_for_position]
                                       [(cos_sim_matrix[i, closeby_indices_for_position] != 1).all()
                                        or (cos_sim_matrix[i, i] != 0.5).all()]
                                       for i in closeby_indices_for_position]))
            #####################################
            color_main_vf.append(cmap(int(100 * (alpha))))
            #####################################
            color_direction.append([np.concatenate((next_color[k],np.array([alpha]))) for k in closeby_indices_for_position
                                    if [[tuple(next_color[i]) for i in closeby_indices_for_position].count(tuple(next_color[k]))]
                                    == np.max([[tuple(next_color[i]) for i in closeby_indices_for_position].count(tuple(next_color[j]))
                                               for j in closeby_indices_for_position])][0])
            color_position.append([np.concatenate((section_cmap[k], np.array([alpha]))) for k in closeby_indices_for_position
                                    if [[tuple(section_cmap[i]) for i in closeby_indices_for_position].count(tuple(section_cmap[k]))]
                                    == np.max([[tuple(section_cmap[i]) for i in closeby_indices_for_position].count(tuple(section_cmap[j]))
                                               for j in closeby_indices_for_position])][0])

    average_directions = np.array(average_directions)
    average_positions = np.array(average_positions)

    #####################################
    ############## Plot  ################
    #####################################
    fig1 = plt.figure(figsize=(10, 5))
    fig2 = plt.figure(figsize=(10, 5))
    gs = gridspec.GridSpec(1, 2, width_ratios=[2*n_components, 2/n_components], height_ratios=[1])
    #color = ['black', 'silver']

    if n_components == 2:
        ax1 = fig1.add_subplot(gs[0])
        ax3 = fig2.add_subplot(gs[0])
        for ax in [ax1,ax3]:
            ax.set_title(title)
            ax.set_aspect(1. / ax.get_data_ratio())
            #ax.set_xticks([])
            #ax.set_yticks([])
        #####################################
        # Plot surface deformations:
        for i in range(len(final_vector)):
            if (final_vector[i] != np.zeros((1,2))[0]).all():
                ax1.arrow(u[i, 0], u[i, 1], final_vector[i, 0], final_vector[i, 1],
                          head_width=0.03, head_length=0.03, linewidth=3, fc=next_color[i], ec=next_color[i])
        ax1.scatter(u[:, 0], u[:, 1], c=section_cmap, s=30)
        #####################################
        # Plot main vector field:
        #for i in range(len(average_directions)):
        #    if (average_directions[i] != np.zeros((1, 2))[0]).all():
        #        ax3.arrow(average_positions[i, 0], average_positions[i, 1],
        #                  average_directions[i, 0], average_directions[i, 1],
        #                  head_width=0.03, head_length=0.03, linewidth=3, fc=color_main_vf[i], ec=color_main_vf[i])
        #####################################
        # Plot average positions/directions with color vector field
        for i in range(len(average_directions)):
            if (average_directions[i] != np.zeros((1, 2))[0]).all():
                ax3.arrow(average_positions[i, 0], average_positions[i, 1],
                          average_directions[i, 0], average_directions[i, 1],
                          head_width=0.03, head_length=0.03, linewidth=3, fc=color_direction[i], ec=color_direction[i])
        ax3.scatter(average_positions[:, 0], average_positions[:, 1], c=color_position, s=30)
        #####################################
        # Get average position/direction pairs (colored accordingly):
        # after nearby points average (better)
        #pos_dir_pairs = np.array([color_position, color_direction])
        # over initial umap (worst, all point end up in the center of the vf)
        #pos_dir_pairs = np.array([section_cmap, next_color])
        #print(pos_dir_pairs.shape)
        #for i in range(np.unique(pos_dir_pairs[:,:,:3], axis=1).shape[1]):
        #    pair = np.unique(pos_dir_pairs[:,:,:3], axis=1)[:,i]
            #print(pair)
        #    avg_pos_dir = [i for i in range(pos_dir_pairs.shape[1]) if (pos_dir_pairs[:,:,:3][:,i] == pair).all()]
            #print(avg_pos_dir)
            #print(average_positions.shape)
        #    ax3.arrow(np.mean(average_positions[avg_pos_dir], axis=0)[0],
        #              np.mean(average_positions[avg_pos_dir], axis=0)[1],
        #              np.mean(average_directions[avg_pos_dir], axis=0)[0]*2,
        #              np.mean(average_directions[avg_pos_dir], axis=0)[1]*2,
        #              head_width=0.04, head_length=0.04, linewidth=4,
        #              fc=pos_dir_pairs[1][avg_pos_dir[0]][:3], ec=pos_dir_pairs[1][avg_pos_dir[0]][:3])
        #    ax3.scatter(np.mean(average_positions[avg_pos_dir], axis=0)[0],
        #                np.mean(average_positions[avg_pos_dir], axis=0)[1],
        #                color=pos_dir_pairs[0][avg_pos_dir[0]][:3], s=200)
        #####################################
        # Plot average trial trajectory:
        # average positions from the same time interval
        # [(x,y), length of longest trajectory, nr subject trajectories]
        avg_trial_trajectory = np.ma.empty((2, max([len(subj) for subj in trajectory_test]), len(trial_subjects)))
        avg_trial_trajectory.mask = True
        for subj, trajectory in enumerate(trajectory_test):
            avg_trial_trajectory[:u[trajectory].T.shape[0], :u[trajectory].T.shape[1], subj] = u[trajectory].T
        avg_trial_trajectory = avg_trial_trajectory.mean(axis=2)
        print(avg_trial_trajectory)

        ax3.plot(avg_trial_trajectory.T[:,0], avg_trial_trajectory.T[:,1], linewidth=1, color='black')

        for subj_trajectory in trajectory_test:
            for i in subj_trajectory:
                ax3.arrow(u[i, 0], u[i, 1], final_vector[i, 0], final_vector[i, 1],
                head_width=0.04, head_length=0.04, linewidth=4, fc=next_color[i], ec=next_color[i])
                ax3.scatter(u[i][0], u[i][1], color=section_cmap[i], edgecolors='black', s=200)

    # get length of each trajectory
        #lengths = [len(subj) for subj in trajectory_test]
        # interpolate to get all trajectories the same length
        #interp_u = []

        #for subj in trajectory_test:
        #    if len(subj) < max(lengths):
        #        print('interpolation')
        #        print(u.shape)
        #        print(u[subj,0])
        #        print(len(u[subj,0]))
        #        print(len(np.arange(0, len([subj]), 1)))
        #        print(u[subj,0].shape)
        #        print(np.arange(0, len([subj]), 1).shape)
        #        interpolator_x = interp1d(np.arange(0, len(u[subj,0]), 1), u[subj,0], kind='linear')(
        #            np.linspace(0, len(subj)-1, max(lengths))[:max(lengths)])
        #        interpolator_y = interp1d(np.arange(0, len(u[subj,1]), 1), u[subj,1], kind='linear')(
        #            np.linspace(0, len(subj)-1, max(lengths))[:max(lengths)])
        #        interp_u.append(np.array((interpolator_x, interpolator_y)))
        #    for i in subj:
        #        if (final_vector[i] != np.zeros((1,2))[0]).all():
        #            ax3.arrow(u[i, 0], u[i, 1], final_vector[i, 0], final_vector[i, 1],
        #            head_width=0.04, head_length=0.04, linewidth=4, fc=next_color[i], ec=next_color[i])
        #        ax3.scatter(u[i][0], u[i][1], color=section_cmap[i], edgecolors='black', s=200)

        #ax3.plot(np.mean(u[:, 0][trajectory_test], axis=0), np.mean(u[:,1][trajectory_test],axis=0), linewidth=1, color='black')
        #print(interp_u)
        #ax3.plot(np.mean(interp_u[:,0], axis=0), np.mean(interp_u[:, 1], axis=0), linewidth=1,
        #     color='black')

    # To do:
    # - up vs. down
    # - 3D

    # plot 2D cmap
    ax2 = fig1.add_subplot(gs[1])
    ax4 = fig2.add_subplot(gs[1])

    for ax in [ax2, ax4]:
        ax.imshow(data_manager.cmap)
        ax.set_aspect('equal')
        ax.set_title('surface\n(top down view)', fontsize=12)
        ax.set_xticks([0, 50, 100])
        ax.set_yticks([0, 50, 100])
        ax.set_xticklabels(['Left', 'Center', 'Right'], fontsize=9)
        ax.set_yticklabels(['Back', 'Middle', 'Front'], fontsize=9)

    fig1.suptitle(suptitle, fontsize=16)
    fig2.suptitle(f"{suptitle} Vector Field", fontsize=16)
    plt.pause(1)
    for fig in [fig1, fig2]:
        fig.tight_layout()
        fig.show()
        plt.pause(0.1)

    #plt.show()
