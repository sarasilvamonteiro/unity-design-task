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

# last_update: 25 Mar 24

class DimRed():

    def __init__(self, IOS=False, Windows=False, features_1=None, features_2=None,
                 subj='all', trial='all', holes='all', hand='all', balanced=True):

        self.IOS = IOS
        self.Windows = Windows
        self.data_manager = ManageData(IOS=self.IOS, Windows=self.Windows)
        # Merge features (e.g. positions and derivative (velocities))
        if type(features_1) != type(None) and type(features_2) != type(None):
            self.features = pd.concat([features_1, features_2], axis=1)
            print(self.features.shape)
        else:
            self.features = features_1

        self.subj = subj
        self.trial = trial
        self.holes = holes
        self.hand = hand
        self.balanced = balanced

        self.trial_data = self.get_trial_data()
        self.trial_syllables = self.trial_data.index.get_level_values('syllable')
        self.trial_number = self.trial_data.index.get_level_values('trial')

        if self.balanced:
            self.balanced_trial_data = self.get_balanced_data()

        self.suptitle = f'Hand: {hand.lower()} Trial: {trial} Holes: {holes}'
        (self.section_cmap, self.up, self.down,
         self.section_to_color, self.color_to_section) = self.get_deformation_info()
        self.umap_data = self.umap()
        self.pca_data = self.pca()
        self.umap_pca_data = self.umap(pca=True)

        # Vector field data:
        (self.color_main_vf, self.vf_positions, self.vf_position_color,
         self.vf_directions, self.vf_direction_color) = self.vector_field()

    def get_trial_data(self, trial=None, hand=None):
        """ Extract trial data. """
        if self.subj == 'all':
            self.subj = self.data_manager.subjects
        if self.trial == 'all' or trial == 'all':
            self.trial = [1,2,3,4,5,6,7]
            trial = self.trial
        if self.holes == 'all':
            self.holes = [1,2]
        if self.hand == 'all' or hand == 'all':
            self.hand = ['Left', 'Right']
            hand = self.hand

        # Check if specific trial or hand was requested
        if type(trial) == type(None):
            trial = self.trial
        if type(hand) == type(None):
            hand = self.hand
        print(trial, hand)
        trial_data = self.features.loc[:, self.features.index.isin(self.data_manager.section_list, level=1),
                     self.subj, trial, self.holes, :, hand]
        return trial_data

    def get_balanced_data(self):
        print(f'Balancing dataset...')
        runs = RandomUnderSampler(random_state=42)
        syllables = self.trial_data.index.get_level_values('syllable')
        data, _ = runs.fit_resample(self.trial_data, syllables)  # out: trial data, trial syllables
        # We need to sort this way so that it is organized in the same order as original dataset
        data = data.sort_index(level='id').sort_index(level=['subject', 'trial', 'holes', 'level_order'])
        labels, counts = np.unique(syllables, return_counts=True)
        nr_samples = dict(zip(labels, counts))
        print(f'nr. samples (balanced): {nr_samples}')
        return data

    def pca(self, n_components=10):
        print(f'Doing PCA...')
        self.pca_components = n_components
        pca_ = PCA(n_components=n_components)
        data = self.get_trial_data()
        if self.balanced:
            data = self.balanced_trial_data
        pca_vals = pca_.fit_transform(data)
        print(f'Done.')
        return pca_vals

    def umap(self, n_neighbors=80, min_dist=0.3, lr=1, metric='euclidean', pca=False, n_components=2):
        print(f'Doing UMAP...')
        self.n_neighbors = n_neighbors
        self.min_dist = min_dist

        data = self.get_trial_data()
        if self.balanced:
            data = self.balanced_trial_data
        if pca:
            data = self.pca_data

        umap_ = umap.UMAP(
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            n_components=n_components,
            metric=metric,
            learning_rate=lr)

        u = umap_.fit_transform(data)
        print('Done.')
        return u

    def get_trajectories(self, trial=None, hand=None):
        print(f'Extracting trajectories...')
        # Despite having umap and everything else for a specific hand,
        # we might want the trajectory considering the two hands,
        # they will be plotted on top of the specific hand clustering.

        # Get current trial info:
        trial_data = self.trial_data
        trial_number = self.trial_number
        # Check if specifit trial or hand was requested:
        if type(trial) == type(None):
            trial = self.trial
        if type(hand) == type(None):
            hand = self.hand
        if trial != self.trial or hand != self.hand:
            print(trial, hand)
            trial_data = self.get_trial_data(trial, hand)
            trial_number = trial_data.index.get_level_values('trial')

        trial_subjects = np.unique(trial_data.index.get_level_values('subject'))
        trajectories = []
        for trial in np.unique(trial_number):
            trial_trajectories = []
            for subj in trial_subjects:
                subj_trajectory = [syllable for syllable in
                                   trial_data.loc[:, :, subj, trial, :, :, :].index.get_level_values('syllable')]
                trial_trajectories.append(subj_trajectory)
            trajectories.append(trial_trajectories)
        print(f'Done.')
        return trajectories

    def average_trajectories(self, trial=None, hand=None):
        print(f'Getting average trajectories...')
        # Check if specific trial or hand was requested
        if type(trial) == type(None):
            trial = self.trial
        if type(hand) == type(None):
            hand = self.hand

        trajectories = self.get_trajectories(trial, hand)
        lengths = [[len(subj_traj) for subj_traj in trial_traj] for trial_traj in trajectories]
        max_length_per_trial = [max([len(subj_traj) for subj_traj in trial_traj if len(subj_traj) != 0])
                                for trial_traj in trajectories]
        # Get average number of syllables per trial
        mean_length_per_trial = [int(np.mean([len(subj_traj) for subj_traj in trial_traj if len(subj_traj) != 0]))
                                 for trial_traj in trajectories]
        print('Average syllables per trial:')
        avg_trajectories = []
        for trial, trial_traj in enumerate(trajectories):
            print(f'trial {trial+1}: {mean_length_per_trial[trial]}')
            avg_trial_traj = []
            for subj_traj in trial_traj:
                # Check that subject did any movement
                if len(subj_traj) == 0:
                    new_traj = []
                    continue
                # Check if movements are less than average
                if len(subj_traj) < mean_length_per_trial[trial]:
                    # Calculate the step size for interpolation
                    step_size = len(subj_traj) / (mean_length_per_trial[trial] - 1)
                    # Perform linear interpolation
                    new_traj = [subj_traj[idx] for idx in [min(int(i * step_size), len(subj_traj) - 1)
                                                           for i in range(mean_length_per_trial[trial])]]
                # Check if movements are more than average
                if len(subj_traj) > mean_length_per_trial[trial]:
                    # Calculate the indices to keep
                    indices_to_keep = np.linspace(0, len(subj_traj) - 1, mean_length_per_trial[trial], dtype=int)
                    # Select elements at calculated indices
                    new_traj = [subj_traj[i] for i in indices_to_keep]
                # Check if it's the same length
                if len(subj_traj) == mean_length_per_trial[trial]:
                    new_traj = subj_traj
                avg_trial_traj.append(new_traj)
            avg_trajectories.append(avg_trial_traj)
        print('Done.')
        return avg_trajectories

    def average_trajectory_per_trial(self, trial=None, hand=None):
        """ Match the syllables from each trajectory to its position/direction color.
        They will later be plotted in the average position/direction corresponding to that syllable. """

        # Check if specific trial or hand was requested
        if type(trial) == type(None):
            trial = self.trial
        if type(hand) == type(None):
            hand = self.hand

        avg_trajectories = self.average_trajectories(trial, hand)
        avg_trajectory_per_trial = []
        # for each trial...
        for trial_traj in avg_trajectories:
            avg_trial = np.zeros((len(trial_traj[0]),), dtype=object)
            # Check every syllable across all subjects for given trial
            for syllable in range(len(trial_traj[0])):
                syllable_at_idx = [subj_traj[syllable] for subj_traj in trial_traj]
                # Count how many syllables are at each index across subjects
                # (each index is a deformation across the trial)
                syllable_values, syllable_counts = np.unique(syllable_at_idx, return_counts=True)
                # Keep the most common syllable amongst subjects for a given trial and order of execution
                most_common_syllable_idx = np.argmax(syllable_counts)
                most_common_syllable = syllable_values[most_common_syllable_idx]
                avg_trial[syllable] = most_common_syllable
            avg_trajectory_per_trial.append(avg_trial)

        # Get positions and colors of each trial's trajectory
        trajectory_color_per_trial = []
        for avg_trial_traj in avg_trajectory_per_trial:
            trial_traj_color = []
            for syllable in avg_trial_traj:
                trial_traj_color.append(self.section_to_color[syllable])
            trajectory_color_per_trial.append(trial_traj_color)

        return avg_trajectory_per_trial, trajectory_color_per_trial

    def get_deformation_info(self):
        """
        :return:
        section_cmap: list, colors by surface section
        up: list, indexes of up deformations
        down: list, indexes of down deformations
        """
        print(f'Getting section info...')
        trial_syllables = self.trial_syllables
        if self.balanced:
            trial_syllables = self.balanced_trial_data.index.get_level_values('syllable')

        # Section info:
        section_cmap = []       # current position color
        up = []; down = []      # indexes for up and down deformations
        section_to_color_dict = {}  # save unique section colors
        color_to_section_dict = {}
        for idx, syllable in enumerate(trial_syllables):
            if syllable[1] in ['F', 'M', 'B']:
                LCR = syllable[0]
                BMF = syllable[1]
            if syllable[1] not in ['F', 'M', 'B']:
                LCR = syllable[0:2]
                BMF = syllable[2]
            color, index = self.data_manager.section_cmap(LCR, BMF, length=100, return_index=True)
            section_cmap.append(color)
            section_to_color_dict[syllable] = color
            color_to_section_dict[tuple(color)] = syllable
            if syllable[-2:] == 'Up':
                up.append(idx)
            if syllable[-4:] == 'Down':
                down.append(idx)
        print('Done.')
        return section_cmap, up, down, section_to_color_dict, color_to_section_dict

    def get_cluster_direction(self, umap=True, pca=True):
        print(f'Getting direction info...')

        trial_number = self.trial_number
        if self.balanced:
            trial_number = self.balanced_trial_data.index.get_level_values('trial')

        #section_cmap, _, _ = self.get_deformation_info()
        if umap and not pca:
            clustered_data = self.umap_data
        if pca and not umap:
            clustered_data = self.pca_data
        if umap and pca:
            clustered_data = self.umap_pca_data

        # Position, direction (vector field), and color computations:
        final_vector = []  # direction
        next_color = []  # next position color (direction)
        # Iterate over all syllables:
        for i in range(len(clustered_data) - 1):
            # Vector pointing at next value (next syllable)
            vector = ((clustered_data[i + 1] - clustered_data[i]) /
                      np.linalg.norm((clustered_data[i + 1] - clustered_data[i])))
            # Next syllable's surface section color (where we're going)
            color = self.section_cmap[i + 1]
            # Check if next trial is different from current
            if trial_number[i + 1] != trial_number[i]:
                # Add zero vector to last syllable of current trial
                vector = np.zeros((1, 2))[0]
                color = self.section_cmap[i]
            final_vector.append(vector)
            next_color.append(color)
        final_vector.append(np.zeros((1, 2))[0])    # Append zero to last syllable of last trial
        next_color.append(self.section_cmap[i])     # Append current color to last syllable of last trial
        final_vector = np.array(final_vector) * 0.7 # Scale final vector
        next_color = np.array(next_color)

        return final_vector, next_color

    def vector_field(self, umap=True, pca=True, vf_min_dist=1):
        print('Creating vector field...')
        self.vf_min_dist = vf_min_dist

        if umap and not pca:
            clustered_data = self.umap_data
        if pca and not umap:
            clustered_data = self.pca_data
        if umap and pca:
            clustered_data = self.umap_pca_data

        final_vector, next_color = self.get_cluster_direction(umap, pca)
        # Define color map for vector field
        cmap = LinearSegmentedColormap.from_list("white_black", [(1, 1, 1), (0, 0, 0)], N=100)
        # Compute cosine similarity matrix between direction vector
        cos_sim_matrix = (cosine_similarity(final_vector) + 1) / 2
        # Compute distance matrix
        distances = np.linalg.norm(clustered_data[:, np.newaxis] - clustered_data, axis=2)
        # Set a threshold for "closeby" positions
        closeby_indices = np.where(distances < self.vf_min_dist)
        print(closeby_indices)
        # Compute average directions for closeby positions
        vf_directions = []
        vf_positions = []
        color_position = []     # average color position (where avg direction starts from)
        color_direction = []    # average color direction (vector field)
        color_main_vf = []      # cmap of avg direction similarity to all directions

        for i in range(len(clustered_data)):
            # Get closeby indices for current syllable (i)
            closeby_indices_for_position = closeby_indices[1][closeby_indices[0] == i]
            # Average position/direction considering all syllables (all umap values)
            if len(closeby_indices_for_position) > 0:
                average_dir = np.mean(final_vector[closeby_indices_for_position], axis=0)
                vf_directions.append(average_dir)
                average_pos = np.mean(clustered_data[closeby_indices_for_position], axis=0)
                vf_positions.append(average_pos)
                # Compute average similarity between all points involved to get the corresponding color
                alpha = np.mean(np.unique([cos_sim_matrix[i, closeby_indices_for_position]
                                           [(cos_sim_matrix[i, closeby_indices_for_position] != 1).all()
                                            or (cos_sim_matrix[i, i] != 0.5).all()]
                                           for i in closeby_indices_for_position]))
                # Get color opacity based on similarity
                color_main_vf.append(cmap(int(100 * (alpha))))
                # Save position/direction colors
                color_direction.append(
                    [np.concatenate((next_color[k], np.array([alpha]))) for k in closeby_indices_for_position
                     if [[tuple(next_color[i]) for i in closeby_indices_for_position].count(tuple(next_color[k]))]
                     == np.max([[tuple(next_color[i]) for i in closeby_indices_for_position].count(tuple(next_color[j]))
                                for j in closeby_indices_for_position])][0])
                color_position.append(
                    [np.concatenate((self.section_cmap[k], np.array([alpha]))) for k in closeby_indices_for_position
                     if [[tuple(self.section_cmap[i]) for i in closeby_indices_for_position].count(tuple(self.section_cmap[k]))]
                     == np.max(
                        [[tuple(self.section_cmap[i]) for i in closeby_indices_for_position].count(tuple(self.section_cmap[j]))
                         for j in closeby_indices_for_position])][0])

        vf_directions = np.array(vf_directions)
        vf_positions = np.array(vf_positions)

        print("Done.")
        return color_main_vf, vf_positions, color_position, vf_directions, color_direction

    def average_position_direction_pairs(self, umap=True, pca=True):

        print('Averaging vector field...')
        # position/direction pairs after cluster averaging
        pos_dir_pairs = np.array([self.vf_position_color, self.vf_direction_color])
        avg_vf_positions = []; avg_vf_directions = []
        avg_vf_position_color = []; avg_vf_direction_color = []
        for i in range(np.unique(pos_dir_pairs[:, :, :3], axis=1).shape[1]):
            # Get unique position/deformation pairs (based on their color)
            pair = np.unique(pos_dir_pairs[:,:,:3], axis=1)[:,i]
            # Get indexes that match that pair
            avg_pos_dir = [i for i in range(pos_dir_pairs.shape[1]) if (pos_dir_pairs[:,:,:3][:,i] == pair).all()]
            # Save positions/directions/colors of those indexes
            avg_vf_positions.append(np.mean(self.vf_positions[avg_pos_dir], axis=0))      # x, y
            avg_vf_directions.append(np.mean(self.vf_directions[avg_pos_dir], axis=0)*2)  # x, y
            avg_vf_position_color.append(pos_dir_pairs[0][avg_pos_dir[0]][:3])
            avg_vf_direction_color.append(pos_dir_pairs[1][avg_pos_dir[0]][:3])
        print("Done.")
        return avg_vf_positions, avg_vf_position_color, avg_vf_directions, avg_vf_direction_color

    def plot_vector_field(self, umap=True, pca=True, trajectory=False, trial=None, hand=None):

        print("Plotting vector field...")
        fig = plt.figure(figsize=(10, 5))
        gs = gridspec.GridSpec(1, 2, width_ratios=[2 * 2, 2 / 2], height_ratios=[1])

        ax = fig.add_subplot(gs[0])
        ax.set_aspect(1. / ax.get_data_ratio())
        ax.set_xticks([])
        ax.set_yticks([])
        # Plot main vector field colored by current and next surface sections
        for i in range(len(self.vf_positions)):
            if (self.vf_directions[i] != np.zeros((1, 2))[0]).all():
                # Plot direction arrow
                ax.arrow(self.vf_positions[i, 0], self.vf_positions[i, 1],
                          self.vf_directions[i, 0], self.vf_directions[i, 1],
                          head_width=0.03, head_length=0.03, linewidth=3,
                          fc=self.vf_direction_color[i], ec=self.vf_direction_color[i])
        # Plot position points
        ax.scatter(self.vf_positions[:, 0], self.vf_positions[:, 1], c=self.vf_position_color, s=30)

        title = (f'(neigh:{self.n_neighbors} min-dist:{self.min_dist} vf-min-dist:{self.vf_min_dist} '
                 f'pca:{str(self.pca_components).lower()}, balance:{str(self.balanced).lower()})')
        ax.set_title(title)

        ax1 = fig.add_subplot(gs[1])
        ax1.imshow(self.data_manager.cmap)
        ax1.set_aspect('equal')
        ax1.set_title('surface\n(top down view)', fontsize=12)
        ax1.set_xticks([0, 50, 100])
        ax1.set_yticks([0, 50, 100])
        ax1.set_xticklabels(['Left', 'Center', 'Right'], fontsize=9)
        ax1.set_yticklabels(['Back', 'Middle', 'Front'], fontsize=9)
        fig.suptitle(f"{self.suptitle} Vector Field", fontsize=16)
        fig.tight_layout()

        if trajectory:
            print("...with trajectory...")
            # Check if specific trial or hand was requested
            if type(trial) == type(None):
                trial = self.trial
            if type(hand) == type(None):
                hand = self.hand

            (avg_cluster_positions, avg_cluster_position_color,
             avg_cluster_directions, avg_cluster_direction_color) = self.average_position_direction_pairs()

            avg_trajectory_per_trial, trajectory_color_per_trial = self.average_trajectory_per_trial(trial, hand)

            for trial_traj in avg_trajectory_per_trial:
                positions = np.zeros((len(trial_traj),2)); directions = np.zeros((len(trial_traj),2))
                position_colors = np.zeros((len(trial_traj),3)); direction_colors = np.zeros((len(trial_traj),3))
                # Check if syllable color is the same as one from the average cluster colors
                # and get its position and direction:
                # All but the last...
                pop_idx = []
                for syllable in np.arange(0, len(trial_traj)-1, 1):
                    # Get current and next syllable colors
                    position_colors[syllable] = self.section_to_color[trial_traj[syllable]]
                    direction_colors[syllable] = self.section_to_color[trial_traj[syllable+1]]
                    # Get position and direction
                    syllable_position_direction = np.array([[avg_cluster_positions[i],avg_cluster_directions[i]]
                                                            for i in range(len(avg_cluster_positions)) if
                                                            ((avg_cluster_position_color[i] == position_colors[syllable]).all() and
                                                             (avg_cluster_direction_color[i] == direction_colors[syllable]).all())])
                    # When using both hands over one hand vf, some syllable transitions dont occur
                    # for now, we ignore them... (fix later)
                    print(syllable_position_direction)
                    try:
                        positions[syllable] = syllable_position_direction[0][0]
                        directions[syllable] = syllable_position_direction[0][1]
                    except:
                        pop_idx.append(syllable)
                # The last
                position_colors[-1] = self.section_to_color[trial_traj[-1]]
                direction_colors[-1] = position_colors[-1]
                positions[-1] = np.array([avg_cluster_positions[i] for i in range(len(avg_cluster_positions)) if
                                 ((avg_cluster_position_color[i] == position_colors[-1]).all() and
                                  (avg_cluster_direction_color[i] == position_colors[-1]).all())])[0]
                directions[-1] = np.zeros(2)
                # Plot trajectory:
                print(positions.shape)
                print(directions.shape)
                # Plot trajectory path
                ids = [i for i in list(range(len(positions))) if i not in pop_idx]
                ax.plot(positions[ids,0], positions[ids,1], linewidth=1, color='black')
                count = 0
                for i in ids:
                    #ax.arrow(positions[i,0], positions[i,1], directions[i,0], directions[i,1],
                    #        head_width=0.04, head_length=0.04, linewidth=4,
                    #        fc=direction_colors[i], ec=direction_colors[i])
                    ax.scatter(positions[i,0], positions[i,1],
                            color=position_colors[i], edgecolors='black', s=200+count)
                    count += 30

        fig.show()
        print("Done.")






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

    print(trial_subjects)
    print(len(trial_data))
    trial = 7
    trajectory_test = [] # [[subj1_trial1], [subj2_trial1], ...]
    for subj in trial_subjects: # get all subjects
        print(subj)
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
            if trajectory != []:
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
