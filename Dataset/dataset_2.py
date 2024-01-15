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

    # NEW:
    # - separate fluid from general
    # - read which spheres were being touched
    # - create automatic dataset of movements from that


    def __init__(self):

        # i should create a file that saves the good subjects and the path of the data
        # the number of spheres and the number of hand joints

        self.path = '/Users/smonteiro/Desktop/DesignMotorTask/Data'
        # new subjects
        #self.subjects = np.arange(1,16,1)
        self.subjects = [5]
        # old subjects
        #self.subjects = np.array([5, 8, 9, 11, 12, 13, 14, 15, 16, 17])
        self.nr_subjects = len(self.subjects)
        self.nr_joints = 31
        self.nr_spheres = 145
        self.section_list = ['LMidUp', 'LFrontUp', 'CFrontUp',
                             'RFrontUp', 'RMidUp', 'RFrontDown',
                             'CFrontDown', 'LFrontDown', 'CBackUp',
                             'CLFront', 'CRFront']
        self.cmap = np.load(f"surface_colormap.npy")

    def section_cmap(self, LCR, BMF):
        """ Indexes of 2D color map (surface top view). """

        # left, center, right
        LCR_dict = {'L': 0, 'CL': 25, 'C': 50, 'CR': 75, 'R': 99}
        # back, middle, front
        BMF_dict = {'B': 0, 'M': 50, 'F': 99}
        section_cmap = self.cmap[BMF_dict[BMF], LCR_dict[LCR]]

        return section_cmap

    #######################
    ##### Import Data #####
    #######################
    def import_general(self, subj, trial, holes, toDataFrame = False):
        # 'C:/Users/teaching lab/Desktop/
        # tree = ET.parse(r"C:\Users\Sara\Desktop\DesignMotorTask\Data\subject_" + str(int(subj))
        #                + "\\" + str(self.holes) + "_holes_1_flows_general_" + str(self.trial))
        tree = ET.parse("" + self.path + "/subject_" + str(int(subj))
                        + "/" + str(holes) + "_holes_1_flows_general_" + str(trial) + ".xml")
        root = tree.getroot()
        print(root)
        if toDataFrame:
            return self.XMLtoDataFrame(root)
        else:
            return root
    def import_hands(self, subj, trial, holes, hand, toDataFrame = False):
        # tree = ET.parse(r"C:\Users\Sara\Desktop\DesignMotorTask\Data\subject_" + str(int(subj))
        #                + "\\" + str(self.holes) + "_holes_1_flows_" + str(hand) + "_hand_data_" + str(self.trial))
        tree = ET.parse(r"" + self.path + "/subject_" + str(int(subj)) + "/" +
                        str(holes) + "_holes_1_flows_" + str(hand) + "_hand_data_" + str(trial) + ".xml")
        root = tree.getroot()

        if toDataFrame:
            return self.XMLtoDataFrame(root)
        else:
            return root
    def import_spheres(self, subj=None, trial=None, holes=None, frame=slice(None), toDataFrame=False):
        # this is just if we want to import initial positions
        if subj == None:
            subj = self.subjects[0]
            holes = 1
            trial = 0
            frame = 0
        # tree = ET.parse(r"C:\Users\Sara\Desktop\DesignMotorTask\Data\subject_" + str(int(subj)) + "\\" + str(
        #    self.holes) + "_holes_1_flows_sphere_position_" + str(self.trial))
        tree = ET.parse(r"" + self.path + "/subject_" + str(int(subj))
                        + "/" + str(holes) + "_holes_1_flows_sphere_position_" + str(trial) + ".xml")
        root = tree.getroot()

        if toDataFrame:
            return self.XMLtoDataFrame(root)
        else:
            return root[frame]

    def import_fluid(self, subj, trial, holes, toDataFrame=False):
        # 'C:/Users/teaching lab/Desktop/
        # tree = ET.parse(r"C:\Users\Sara\Desktop\DesignMotorTask\Data\subject_" + str(int(subj))
        #                + "\\" + str(self.holes) + "_holes_1_flows_general_" + str(self.trial))
        tree = ET.parse(r"" + self.path + "/subject_" + str(int(subj))
                        + "/" + str(holes) + "_holes_1_flows_fluid_" + str(trial) + ".xml")
        root = tree.getroot()

        if toDataFrame:
            return self.XMLtoDataFrame(root)
        else:
            return root

    ####### Read XML #######
    def XMLtoDataFrame(self, root):

        # create an empty DataFrame to store the data
        df_columns = []
        df_data = []

        for child in root:
            row_data = {}
            for element in child:
                if len(element) == 0:
                    row_data[element.tag] = element.text
                # check if column has nested columns (e.g. x,y,z)
                else:
                    row_data_1 = {}
                    for axis in element:
                        print(axis)
                        row_data_1[axis.tag] = axis.text
                    row_data[element.tag] = row_data_1


                if element.tag not in df_columns:
                    df_columns.append(element.tag)
            df_data.append(row_data)
        # Pandas DataFrame
        df = pd.DataFrame(df_data, columns=df_columns)

        #for child in root:
        #    for element in child:
        #        if len(element) > 0:
        #            result = pd.json_normalize(df[element.tag])
        #            df[element.tag].columns = result.columns

        return df





    #####################

    def import_spheres_to_array(self, subj=None, trial=None, holes=None, frame=slice(None)):

        import_positions = self.import_spheres(subj, trial, holes, frame)
        positions = np.zeros((self.nr_spheres, 3))
        for sphere in np.arange(0, 2 * self.nr_spheres, 2):
            sphere_data = import_positions[sphere]
            for axis, position in enumerate(sphere_data):
                positions[int(sphere / 2)][axis] = float(position.text)

        return positions

    def get_sphere_id(self, sphere_info):
        """ Sphere ID (correct id for aug23). """
        sphere_id = int(sphere_info.tag[-4:])
        correct_id = int(
            2000 + (sphere_id - 2000) / 2)  # fix sphere id (apply to aug23 data, it has duplicated sphere data)
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
            hand_dict = {0: 'right', 1: 'left', 2: 'both'}
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
            for [trial, holes] in trial_info.apply(lambda row: [row['Trial'], row['Holes']], axis=1):

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
                    frame_position = np.zeros((self.nr_spheres, 3))
                    timestamp = float(sphere_data[frame][-2].text)

                    # nr_sphere * 2 (aug23, duplicated data mistake)
                    for sphere in np.arange(0, 2 * self.nr_spheres, 2):
                        sphere_info = sphere_data[frame][sphere]
                        for axis, position in zip(range(3), sphere_info):
                            # i/2 because of dup. data mistake
                            frame_position[int(sphere / 2)][axis] = float(position.text)

                        if np.linalg.norm(frame_position[int(sphere / 2)] -
                                          last_positions[int(sphere / 2)]) > 0.005:  # 0.01:
                            # if (frame_position[int(sphere/2)] != last_positions[int(sphere/2)]).any():
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
                new_data = pd.read_excel(ManageData().path + '/' + filename)
                data = pd.concat([data, new_data], ignore_index=True)
        return data

    def load_syllables(self, object):
        """
        :param object: str, 'hands', 'surface' or 'eyes'
        """
        object_syllables = pd.read_pickle(object + '_syllables')
        return object_syllables

    def load_preprocessed_syllables(self, object):
        """
        :param object: str, 'hands', 'surface' or 'eyes'
        """
        object_syllables = pd.read_pickle(object + '_preprocessed_syllables')
        return object_syllables

    def load_surface_moving(self):
        surface_moving = pd.read_pickle('surface_moving')
        return surface_moving

    def preprocess(self, data, norm_position=True, norm_time=True, resample=True,
                   normalizer=preprocessing.MinMaxScaler(), length=100, kind='linear'):
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
                # if len(syllable) < 2:
                #    continue
                # new dataframe
                preprocess = pd.DataFrame(columns=syllable.columns, index=range(length))
                # array of current lenght
                sample_length = np.arange(0, len(syllable), 1)
                # array of resampled length
                new_length = np.arange(0, len(syllable) - 1, (len(syllable) - 1) / length)[:length]
                # apply interpolation over each axis (x,y,z)
                for axis in syllable.iloc[:, ]:
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
                                     'holes': index[2],
                                     'level_order': index[3],
                                     'hand': index[4],
                                     'syllable': index[5],
                                     'features': []}])
            features = []
            for inner_df in data.iloc[row][1:]:
                features.append(inner_df[['x', 'y', 'z', 'time']].values)
            new_row['features'][0] = np.array(features).flatten()
            values = pd.concat([values, new_row], ignore_index=True)

        first_level_values = values['syllable']
        factorized_values, unique_labels = pd.factorize(first_level_values)
        # label_series = pd.Series(factorized_values, index=first_level_values).reset_index(drop=True).rename('syllable')
        values = values.set_index(['subject', 'trial', 'holes', 'level_order', 'hand', 'syllable'])
        values = values['features'].apply(pd.Series)
        values.insert(0, 'time_interval', data['time_interval'])
        values.insert(1, 'labels', factorized_values)
        # values = values.set_index(['hand'])['features'].apply(pd.Series)
        # return values as array
        if as_array:
            return values.values.reshape(-1, len(values.columns))
        # return values as DataFrame
        else:
            return values




    # check hand and surface labels
    # i can just load normally spheres and check if hand is touching it....
    # i can just load hands and check if is touching a sphere....





    def new_syllables(self):


        syllables_df = pd.DataFrame()


        for subj in self.subjects:
            for trial in np.arange(0,7,1):
                for holes in np.arange(1,3,1):

                    general_data = self.import_general(subj,trial,holes, toDataFrame=True)
                    surface_data = self.import_spheres(subj,trial,holes, toDataFrame=True)
                    Lhand_data = self.import_hands(subj,trial,holes,'left', toDataFrame=True)
                    Rhand_data = self.import_hands(subj,trial,holes,'right', toDataFrame=True)


                    Lhand_touch = [i for i,v in enumerate(general_data['LeftHand']) if v == 'true']
                    Rhand_touch = [i for i,v in enumerate(general_data['RightHand']) if v == 'true']

                    syllable = 0
                    L_syllables = {0:[]}
                    R_syllables = {0: []}


                    for i in range(len(general_data['LeftHand'])):

                        # get v two frames before and two frames after movement
                        if i + 2 in Lhand_touch or i - 2 in Lhand_touch:
                            L_syllables[syllable].append(i)

                        if i + 2 in Rhand_touch or i - 2 in Rhand_touch:
                            R_syllables[syllable].append(i)

                        else:
                            syllable += 1
                            L_syllables[syllable] = []
                            R_syllables[syllable] = []


                    #for i,v in enumerate(Rhand_touch):
                    #    if i == 0:
                    #        continue
                    #    if v <= Rhand_touch[i-1] + 2:
                    #        R_syllables[R_syllable].append(v)
                    #    else:
                    #        R_syllable += 1
                    #        R_syllables[R_syllable] = []


                    for syllable in L_syllables.keys():

                        new_syllable = pd.DataFrame()
                        new_syllable = surface_data.iloc[L_syllables[syllable], :-3]
                        #for column in surface_data.columns[:-3]:
                        #    new_col = pd.DataFrame([{column: pd.json_normalize(surface_data.iloc[L_syllables[syllable]][column])}])
                        #    new_syllable = pd.concat([new_syllable, new_col], axis=1)

                        new_syllable = new_syllable.assign(syllable=syllable, subj=int(subj), trial=int(trial), holes=int(holes), hand='Left')
                        syllables_df = pd.concat([syllables_df, new_syllable], ignore_index=True)

                    for syllable in R_syllables.keys():

                        new_syllable = pd.DataFrame()
                        new_syllable = surface_data.iloc[R_syllables[syllable], :-3]
                        #for column in surface_data.columns[:-3]:
                        #    new_col = pd.DataFrame(
                        #        [{column: pd.json_normalize(surface_data.iloc[R_syllables[syllable]][column])}])
                        #    new_syllable = pd.concat([new_syllable, new_col], axis=1)

                        new_syllable = new_syllable.assign(syllable=syllable, subj=int(subj), trial=int(trial), holes=int(holes),
                                                           hand='Right')
                        syllables_df = pd.concat([syllables_df, new_syllable], ignore_index=True)

                        #new_syllable = surface_data.iloc[L_syllables[syllable], :-3]
                        #new_syllable = pd.concat([pd.json_normalize(surface_data.iloc[L_syllables[syllable], :-3][column]) for column in surface_data.columns[:-3]], axis=1)
                        #new_syllable = pd.concat([new_syllable, surface_data.iloc[L_syllables[syllable]]], axis=1)



                    return  syllables_df.set_index(['syllable','subj', 'trial', 'holes', 'hand']).sort_values(by='syllable')




    def touched_spheres(self):

        # create a dataframe for all trials and a

        touched_spheres_df = pd.DataFrame()
        touched_spheres_list = []


        touched_spheres_df.columns = ['subj', 'trial', 'holes', 'order', 'sphere', 'timestamp']

        for subj in self.subjects:
            for trial in np.arange(0,7,1):
                for holes in np.arange(1,3,1):

                    general_data = self.import_general(subj,trial,holes, toDataFrame=True)
                    surface_data = self.import_spheres(subj,trial,holes, toDataFrame=True)
                    Lhand_data = self.import_hands(subj,trial,holes,'left')
                    Rhand_data = self.import_hands(subj,trial,holes,'right')

                    touched_spheres = general_data['TouchedSpheres']

                    for spheres_list in touched_spheres:
                        spheres_list = spheres_list.split(',')



                        for sphere in spheres_list:

                            sphere_data = surface_data[f'Sphere{sphere}']

                            #for frame in sphere_data:

























