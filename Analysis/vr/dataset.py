import xml.etree.ElementTree as ET
import copy
import numpy as np
import pandas as pd
import os
from sklearn import preprocessing
from scipy.interpolate import interp1d


class ManageData():

    """
    Functions to run before anything:
        - save_syllables(): creates dataframe with syllable info for hand, surface, eyes
        (save.syllables() uses surface.moving() to check if surface is moving or not.
        It will automatically run the first time and save moving time/frames as a dataframe.
        The next times it will be loaded from load_surface_moving(), which can also be independently loaded.)
    """

    def __init__(self):

        # i should create a file that saves the good subjects and the path of the data
        # the number of spheres and the number of hand joints

        self.path = '/Users/smonteiro/Desktop/DesignMotorTask/Data'
        self.subjects = np.array([5,8,9,11,12,13,14,15,16,17])
        self.nr_subjects = 10
        self.nr_joints = 31
        self.nr_spheres = 145
        self.section_list = ['LMidUp', 'LFrontUp','CFrontUp',
                             'RFrontUp', 'RMidUp', 'RFrontDown',
                             'CFrontDown', 'LFrontDown', 'CBackUp',
                             'CLFront', 'CRFront']
        self.cmap = np.load('surface_colormap.npy')


    def section_cmap(self, LCR, BFM):

        LCR_dict = {'L': 0,
                    'CL': 25,
                    'C': 50,
                    'CR': 75,
                    'R': 99}

        BFM_dict = {'B': 0,
                    'M': 50,
                    'F': 99}

        section_cmap = self.cmap[BFM_dict[BFM],LCR_dict[LCR]]
        return section_cmap


    def import_hands(self, subj, trial, holes, hand):

        #tree = ET.parse(r"C:\Users\Sara\Desktop\DesignMotorTask\Data\subject_" + str(int(subj))
        #                + "\\" + str(self.holes) + "_holes_1_flows_" + str(hand) + "_hand_data_" + str(self.trial))
        tree = ET.parse(r""+self.path+"/subject_" + str(int(subj)) + "/" +
                        str(holes) + "_holes_1_flows_" + str(hand) + "_hand_data_" + str(trial)+".xml")
        return tree.getroot()

    def import_spheres(self, subj=None, trial=None, holes=None, frame = slice(None)):

        # this is just if we want to import initial positions
        if subj == None:
            subj = self.subjects[0]
            holes = 1
            trial = 0
            frame = 0

        #tree = ET.parse(r"C:\Users\Sara\Desktop\DesignMotorTask\Data\subject_" + str(int(subj)) + "\\" + str(
        #    self.holes) + "_holes_1_flows_sphere_position_" + str(self.trial))
        tree = ET.parse(r""+self.path+"/subject_" + str(int(subj))
                        + "/" + str(holes) + "_holes_1_flows_sphere_position_" + str(trial) +".xml")
        return tree.getroot()[frame]

    def import_general(self, subj, trial, holes):

        #'C:/Users/teaching lab/Desktop/
        #tree = ET.parse(r"C:\Users\Sara\Desktop\DesignMotorTask\Data\subject_" + str(int(subj))
        #                + "\\" + str(self.holes) + "_holes_1_flows_general_" + str(self.trial))
        tree = ET.parse(r""+self.path+"/subject_" + str(int(subj))
                        + "/" + str(holes) + "_holes_1_flows_general_" + str(trial) + ".xml")
        return tree.getroot()

    def import_spheres_to_array(self, subj=None, trial=None, holes=None, frame = slice(None)):

        import_positions = self.import_spheres(subj, trial, holes, frame)
        positions = np.zeros((self.nr_spheres,3))
        for sphere in np.arange(0,2*self.nr_spheres,2):
            sphere_data = import_positions[sphere]
            for axis, position in enumerate(sphere_data):
                positions[int(sphere/2)][axis] = float(position.text)

        return positions


    def get_sphere_id(self, sphere_info):
        """ Sphere ID (correct id for aug23). """
        sphere_id = int(sphere_info.tag[-4:])
        correct_id = int(2000 + (sphere_id - 2000) /2) # fix sphere id (apply to aug23 data, it has duplicated sphere data)
        return sphere_id, correct_id


    def get_hand_id(self, hand):
        '''
        Hand index and colormap dictionary.
        :param hand: str, int; hand input to get corresponding id/name from.
        :return: hand name (str) or hand id (int) retrieved from the dictionary given the hand input.
        '''
        hand_dict = {'right': 0, 'left': 1, 'both': 2}
        color_dict = {'left': 'pink', 'right': 'Reds_r', 'both': 'viridis'}
        if type(hand) == type(0):
            hand_dict = {0: 'right',  1: 'left', 2: 'both'}
            return hand_dict[hand], color_dict[hand_dict[hand]]
        else:
            return hand_dict[hand], color_dict[hand]



    def surface_moving(self):
        """
        Surface moving means that hands are also touching the surface.
        :return: moving timestamps and frames
        """

        moving_df = pd.DataFrame()

        for subj in self.subjects:

            shown = 0
            trial_info = self.load_info(subj)
            last_holes = trial_info['Holes'][0]
            for [trial, holes] in trial_info.apply(lambda row: [row['Trial'] , row['Holes']], axis=1):

                print(subj, trial, holes)

                if holes != last_holes:
                    shown += 1

                last_holes = holes
                # first last positions is initial spheres positions
                last_positions = self.import_spheres_to_array()

                sphere_data = self.import_spheres(subj, trial, holes)
                frames = len(sphere_data)
                moving_timestamps = []
                moving_frames = []

                for frame in range(frames):
                    print(frame)
                    frame_position = np.zeros((self.nr_spheres,3))
                    timestamp = float(sphere_data[frame][-2].text)

                    # nr_sphere * 2 (aug23, duplicated data mistake)
                    for sphere in np.arange(0,2*self.nr_spheres,2):
                        sphere_info = sphere_data[frame][sphere]
                        for axis, position in zip(range(3), sphere_info):
                            # i/2 because of dup. data mistake
                            frame_position[int(sphere/2)][axis] = float(position.text)

                        if np.linalg.norm(frame_position[int(sphere/2)] -
                                          last_positions[int(sphere/2)]) > 0.005:#0.01:
                        #if (frame_position[int(sphere/2)] != last_positions[int(sphere/2)]).any():
                            print('different')
                            moving_timestamps.append(timestamp)
                            moving_frames.append(frame)
                            last_positions = self.import_spheres_to_array(subj, trial, holes, frame)
                            break

                new_row = pd.DataFrame([{'subject': subj,
                                         'trial': trial,
                                         'holes': holes,
                                         'level_order': shown,
                                         'moving_timestamps': moving_timestamps,
                                         'moving_frames': moving_frames}])
                moving_df = pd.concat([moving_df, new_row], ignore_index=True)

        moving_df.to_pickle('surface_moving')
        return moving_df


    def generate_syllables(self):
        """
        Get hand labeled data from each subject's trial videos and get hand/surface/eye positions/time
        for instances where deformations are occurring (syllables).
        :return: DataFrame, positions/time for the whole syllable
        (syllable = whole movement since hand starts moving until it stops/changes intention;
        note: at the beginning and end, surface is not yet being deformed. For that, combine with moving timestamps.)
        """

        def fetch_positions(number_of_points, object_data):
            """
            Iterate over each measured point (i.e., hand joints, spheres, eyes) and get their 3D coordinates
            and corresponding timestamp for each syllable.
            :param number_of_points: range(int), number of measured points for each object
            :param object_data: object data for a given trial, subj, hole (object = {hand, surface, eye}
            :return: DataFrame row, positions/time for each new syllable
            """

            # iterate over every joint/sphere/eye (from object_data)
            for point in number_of_points:
                if point == 0:
                    empty_hand = True
                    new_row = pd.DataFrame([{'subject': subj,
                                             'trial': trial,
                                             'holes':holes,
                                             'level_order': shown,
                                             'syllable': feature,
                                             'hand': hand_title,
                                             'time_interval': [feature_i[interval], feature_f[interval]]}])
                time = []; positions = []; moving = []
                # iterate over each row
                for frame in range(len(general_data)):
                    point_ = object_data[frame][point]
                    timestamp = float(general_data[frame][-3].text)
                    # get the frames that fit in the feature interval
                    if timestamp >= feature_i[interval] and timestamp < feature_f[interval]:
                        # if hand was tracked:
                        if general_data[frame][hand_id].text == 'true' and labeled_data.hand[interval] == \
                                self.get_hand_id(-hand_id - 1)[0]:
                            position_ = np.zeros(3)
                            for axis, position in zip(range(3), point_):
                                position_[axis] = float(position.text)
                            time.append(timestamp)
                            positions.append(position_)
                            # check if surface is moving during this timestamp
                            if np.round(timestamp,1) in np.round(surface_moving.loc[(surface_moving['subject'] == subj)
                                                                                    & (surface_moving['trial'] == trial)
                                                                                    & (surface_moving['holes'] == holes)]['moving_timestamps'].iloc[0],1):
                                moving.append(True)
                            else:
                                moving.append(False)

                positions = np.array(positions)
                
                # we need more than one timestamp to capture movement
                if len(positions) > 1:
                    point_id = point_.tag
                    # fix sphere id (delete in the future)
                    if point_.tag[:6] == 'Sphere':
                        sphere_id, correct_id = self.get_sphere_id(point_)
                        point_id = 'Sphere' + str(correct_id)
                    new_syllable = pd.DataFrame([{point_id : pd.DataFrame({'x':positions[:,0],
                                                                           'y':positions[:,1],
                                                                           'z':positions[:,2],
                                                                           'time':time,
                                                                           'moving': moving})}])
                    new_row = pd.concat([new_row, new_syllable], axis=1)
                    empty_hand = False

            return new_row, empty_hand


        # get surface moving timestamps
        try:
            surface_moving = self.load_surface_moving()
        except:
            print('Running surface_moving() to fetch moving timestamps.')
            surface_moving = self.surface_moving()
        # get subject hand labeled data
        labeled_data = self.load_labeled_data()
        # whole data for hands [0] and surface [1]
        whole_movement = [pd.DataFrame(), pd.DataFrame()]
        # iterate over each surface section in list
        for feature in self.section_list:
            print(feature)
            # try if feature is in data
            try:
                feature_i = labeled_data[feature + '_i']
                feature_f = labeled_data[feature + '_f']
            except:
                pass

            last_data = [-1, -1, -1]
            sequence = -1
            # iterate over rows in data
            for subj, trial, holes, interval in zip(labeled_data.subject, labeled_data.trial,
                                                    labeled_data.holes, range(len(feature_i))):
                # replace this with something that reads the information.txt file to know if its first or last
                # maybe in Trial() we could have a function that reads this file and keeps it as a variable
                if subj != last_data[0]:
                    shown = -1
                if [subj, holes] != [last_data[i] for i in [0,2]]:
                    shown += 1
                # if feature row values aren't nan
                if not np.isnan(feature_i[interval]):
                    sequence += 1
                    # import new data if trial is different
                    if [subj, trial, holes] != last_data:
                        data_list = []
                        # import general data
                        general_data = self.import_general(subj, trial, holes)
                        # hands
                        data_list.append(self.import_hands(subj, trial, holes, hand='right'))  # 1 # 0
                        data_list.append(self.import_hands(subj, trial, holes, hand='left'))  # 2 # 1
                        # import surface data
                        surface_data = self.import_spheres(subj, trial, holes)
                    # iterate over R and L hands
                    for i, hand_data in enumerate(data_list):
                        # -2 for left, -1 for right
                        hand_id = -(i + 1)  # left i > right i
                        hand_title = general_data[0][hand_id].tag[:-4]
                        hand_syllables, empty_hand = fetch_positions(range(self.nr_joints), hand_data)
                        # iterate over each sphere (fix this because there are no repeated spheres anymore)
                        surface_syllables, empty_hand = fetch_positions(np.arange(0, 2 * self.nr_spheres, 2), surface_data)
                        if not empty_hand:
                            whole_movement[0] = pd.concat([whole_movement[0], hand_syllables], ignore_index=True)
                            whole_movement[1] = pd.concat([whole_movement[1], surface_syllables], ignore_index=True)

                last_data = [subj, trial, holes]

        whole_movement[0].sort_values(by=['subject']).set_index(['subject','trial', 'holes', 'level_order', 'hand', 'syllable']).to_pickle('hands_syllables')
        whole_movement[1].sort_values(by=['subject']).set_index(['subject','trial', 'holes', 'level_order', 'hand', 'syllable']).to_pickle('surface_syllables')
        return whole_movement



    def load_info(self, subj):
        info = pd.read_csv(self.path + '/subject_' + str(subj) + '/information.txt', sep=" ")
        return info

    def load_labeled_data(self):
        """
        So far, only subj 12 and 14 have been labeled for their movements.
        :return: dataframe of time intervals for each movement syllable and corresponding trials.
        """
        data = pd.DataFrame()
        for filename in os.listdir(ManageData().path):
            if 'feature_extraction.xlsx' in filename:
                new_data = pd.read_excel(ManageData().path + '/' +filename)
                data = pd.concat([data, new_data], ignore_index=True)
        return data

    def load_syllables(self, object):
        """
        :param object: str, 'hands', 'surface' or 'eyes'
        """
        object_syllables = pd.read_pickle( object + '_syllables')
        return object_syllables

    def load_preprocessed_syllables(self, object):
        """
        :param object: str, 'hands', 'surface' or 'eyes'
        """
        object_syllables = pd.read_pickle( object + '_preprocessed_syllables')
        return object_syllables

    def load_surface_moving(self):
        surface_moving = pd.read_pickle('surface_moving')
        return surface_moving




    def preprocess(self, data, norm_position=True, norm_time=True, resample=True, normalizer = preprocessing.MinMaxScaler(), length=100, kind='linear'):
        """
        Applies normalization and resampling to the x,y,z,time data for all recorded points from data.
        :param data: DataFrame; hands or surface data to resample
        :param norm_position: bool; True to normalize x,y,z (default=True)
        :param norm_time: bool; True to normalize time (default=True)
        :param resample: bool; True to resample (default=True)
        :param normalizer: sklearn.preprocessing; type of scaler (default=MinMaxScaler()
        :param length: int; new number of samples per syllable (default=100)
        :param kind: str; type of interpolation, e.g. 'linear', 'quadratic', 'cubic'
        :return: DataFrame; resampled data
        """

        if 'PalmPosition' in data.columns:
            object = 'hands'
        if 'Sphere2000' in data.columns:
            object = 'surface'


        # we need to copy the original data so that it doesn't change the original
        preprocessed_data = copy.deepcopy(data)
        for column in data.iloc[:, 1:]:
            for i, syllable in enumerate(data[column]):
                if resample == False:
                    length = len(syllable)
                # continue if only one timeframe was recorded
                #if len(syllable) < 2:
                #    continue  
                # new dataframe
                preprocess = pd.DataFrame(columns=syllable.columns, index=range(length))
                # array of current lenght
                sample_length = np.arange(0,len(syllable),1)
                # array of resampled length
                new_length = np.arange(0, len(syllable)-1, (len(syllable)-1)/length)[:length]
                # apply interpolation over each axis (x,y,z)
                for axis in syllable.iloc[:,]:
                    interpolator = interp1d(sample_length, syllable[axis], kind=kind)(new_length)
                    preprocess[axis] = interpolator
                # convert float to bool
                preprocess['moving'] = preprocess['moving'].astype(bool)
                if norm_position:
                    preprocess.iloc[:, :3] = normalizer.fit_transform(preprocess.iloc[:, :3])
                if norm_time:
                    preprocess.iloc[:, 3:4] = normalizer.fit_transform(preprocess.iloc[:, 3:4])
                # substitute unsampled data by sampled data
                preprocessed_data[column].iloc[i] = preprocess
        preprocessed_data.to_pickle(str(object) + '_preprocessed_syllables')
        return preprocessed_data


    def extract_values(self, data, as_array=False):


        data = data.sort_values(by='syllable')
        values = pd.DataFrame()
        for row, index in enumerate(data.index):
            # dropp all columns from dataframe and add a new column with those values
            new_row = pd.DataFrame([{'subject': index[0],
                                     'trial': index[1],
                                     'holes':index[2],
                                     'level_order': index[3],
                                     'hand': index[4],
                                     'syllable': index[5],
                                     'features': []}])
            features = []
            for inner_df in data.iloc[row][1:]:
                features.append(inner_df[['x','y','z','time']].values)
            new_row['features'][0] = np.array(features).flatten()
            values = pd.concat([values, new_row], ignore_index=True)

        first_level_values = values['syllable']
        factorized_values, unique_labels = pd.factorize(first_level_values)
        #label_series = pd.Series(factorized_values, index=first_level_values).reset_index(drop=True).rename('syllable')
        values = values.set_index(['subject','trial', 'holes', 'level_order', 'hand', 'syllable'])
        values = values['features'].apply(pd.Series)
        values.insert(0, 'time_interval', data['time_interval'])
        values.insert(1,'labels',factorized_values)
        #values = values.set_index(['hand'])['features'].apply(pd.Series)
        # return values as array
        if as_array:
            return values.values.reshape(-1, len(values.columns))
        # return values as DataFrame
        else:
            return values











