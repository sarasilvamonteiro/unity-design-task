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

        self.IOS = False
        self.Windows = True
        if self.IOS:
            self.path = '/Users/smonteiro/Desktop/DesignMotorTask/Data'
        if self.Windows:
            self.path = r"C:\Users\Sara\Desktop\DesignMotorTask\Data"
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
        self.cmap = np.load("./main/surface_colormap.npy")

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
        if self.IOS:
            tree = ET.parse("" + self.path + "/subject_" + str(int(subj))
                            + "/" + str(holes) + "_holes_1_flows_general_" + str(trial) + ".xml")
        if self.Windows:
            tree = ET.parse(self.path + "\subject_" + str(int(subj))
                            + "\\" + str(holes) + "_holes_1_flows_general_" + str(trial))
        root = tree.getroot()

        if toDataFrame:
            return self.XMLtoDataFrame(root)
        else:
            return root
    def import_hands(self, subj, trial, holes, hand, toDataFrame = False):
        if self.IOS:
            tree = ET.parse(r"" + self.path + "/subject_" + str(int(subj)) + "/" +
                             str(holes) + "_holes_1_flows_" + str(hand) + "_hand_" + str(trial) + ".xml")
        if self.Windows:
            tree = ET.parse(self.path + "\subject_" + str(int(subj))
                            + "\\" + str(holes) + "_holes_1_flows_" + str(hand) + "_hand_" + str(trial))
        root = tree.getroot()

        if toDataFrame:
            return self.XMLtoDataFrame(root)
        else:
            return root
    def import_surface(self, subj=None, trial=None, holes=None, frame=slice(None), toDataFrame=False):
        # this is just if we want to import initial positions
        if subj == None:
            subj = self.subjects[0]
            holes = 1
            trial = 1
            frame = 0

        if self.IOS:
            tree = ET.parse(r"" + self.path + "/subject_" + str(int(subj))
                            + "/" + str(holes) + "_holes_1_flows_surface_" + str(trial) + ".xml")
        if self.Windows:
            tree = ET.parse(self.path + "\subject_" + str(int(subj)) + "\\" + str(holes) + "_holes_1_flows_surface_" + str(trial))
        root = tree.getroot()

        if toDataFrame:
            return self.XMLtoDataFrame(root)
        else:
            return root[frame]

    def import_fluid(self, subj, trial, holes, toDataFrame=False):
        if self.IOS:
            tree = ET.parse(r"" + self.path + "/subject_" + str(int(subj))
                            + "/" + str(holes) + "_holes_1_flows_fluid_" + str(trial) + ".xml")
        if self.Windows:
            tree = ET.parse(self.path + "\subject_" + str(int(subj))
                            + "\\" + str(holes) + "_holes_1_flows_fluid_" + str(trial))
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

        # do something like this if you want to keep a dataframe
        # inside the main columns (not recommendable, takes longer)
        #for child in root:
        #    for element in child:
        #        if len(element) > 0:
        #            result = pd.json_normalize(df[element.tag])
        #            df[element.tag].columns = result.columns

        return df
    #####################

    def import_spheres_to_array(self, subj=None, trial=None, holes=None, frame=slice(None)):

        import_positions = self.import_surface(subj, trial, holes, frame)
        positions = np.zeros((self.nr_spheres, 3))
        for sphere in range(self.nr_spheres):
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



    def get_syllables(self):
        """
        """

        timestamps_df = pd.DataFrame()
        surface_syllables_df = pd.DataFrame()
        hand_syllables_df = pd.DataFrame()

        def save_to_syllable_df(object_data, object_df, hand):

            new_syllable = pd.DataFrame(object_data.iloc[frame, list(range(object_data.shape[1]-3)) + [object_data.shape[1]-1]]).T
            columns_dict = {'hand': hand, 'level_order': shown, 'holes': int(holes),
                            'trial': int(trial), 'subject': int(subj), 'syllable': syllable}
            for col_name, col_value in columns_dict.items():
                new_syllable.insert(0, col_name, col_value)
            object_df = pd.concat([object_df, new_syllable], ignore_index=True)

            return object_df


        for subj in self.subjects:

            shown = 0
            trial_info = self.load_info(subj)
            last_holes = trial_info['Holes'][0] # first level shown (1 or 2 holes)
            for [trial, holes] in [[1, 1]]:

            #for [trial, holes] in trial_info.apply(lambda row: [row['Trial'], row['Holes']], axis=1):
                # check level order
                print(subj, trial, holes)
                if holes != last_holes:
                    shown += 1
                last_holes = holes

                # import data
                general_data = self.import_general(subj, trial, holes, toDataFrame=True)
                surface_data = self.import_surface(subj, trial, holes, toDataFrame=True)
                Lhand_data = self.import_hands(subj, trial, holes, 'left', toDataFrame=True)
                Rhand_data = self.import_hands(subj, trial, holes, 'right', toDataFrame=True)
                # get indexes where touches are true (deformation occurs)
                L_touch = [i for i, v in enumerate(surface_data['LTouch']) if v == 'true']
                R_touch = [i for i, v in enumerate(surface_data['RTouch']) if v == 'true']
                # initialize syllable count
                syllable = 0
                last_syllable = syllable

                # save data when deformation occurs
                for frame in range(len(general_data)):
                    touch = False
                    print(syllable, frame)
                    # get two frames before and two frames after deformation
                    # check if frame is in deformation indexes
                    if any([f in L_touch for f in np.arange(frame-1, frame+2, 1)]):
                        ### save just timestamps ###
                        #timestamps_df = save_to_syllable_df(general_data.iloc[frame, -1], timestamps_df, hand='Left')
                        ### save surface syllables ###
                        surface_syllables_df = save_to_syllable_df(surface_data, surface_syllables_df, hand='Left')
                        ### save hand syllables ###
                        hand_syllables_df = save_to_syllable_df(Lhand_data, hand_syllables_df, hand='Left')
                        # update last_syllable
                        last_syllable = syllable
                        touch = True
                    if any([f in R_touch for f in np.arange(frame-1, frame+2, 1)]):
                        ### save just timestamps ###
                        #timestamps_df = save_to_syllable_df(general_data.iloc[frame, -1], timestamps_df, hand='Right')
                        ### save surface syllables ###
                        surface_syllables_df = save_to_syllable_df(surface_data, surface_syllables_df, hand='Right')
                        ### save hand syllables ###
                        hand_syllables_df = save_to_syllable_df(Rhand_data, hand_syllables_df, hand='Right')
                        # update last_syllable
                        last_syllable = syllable
                        touch = True

                    if not touch:
                        touch = False
                        syllable = last_syllable + 1

        # save syllables
        surface_syllables_df.set_index(['syllable','subject','trial', 'holes', 'level_order', 'hand']).to_pickle('surface_syllables')
        hand_syllables_df.set_index(['syllable','subject','trial', 'holes', 'level_order', 'hand']).to_pickle('hand_syllables')
        # ..............





    def load_info(self, subj):
        info = pd.read_csv(self.path + '/subject_' + str(subj) + '/information.txt', sep=" ")
        return info


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




    def touched_spheres(self):

        # create a dataframe for all trials and a

        touched_spheres_df = pd.DataFrame()
        touched_spheres_list = []


        touched_spheres_df.columns = ['subj', 'trial', 'holes', 'order', 'sphere', 'timestamp']

        for subj in self.subjects:
            for trial in np.arange(0,7,1):
                for holes in np.arange(1,3,1):

                    general_data = self.import_general(subj,trial,holes, toDataFrame=True)
                    surface_data = self.import_surface(subj,trial,holes, toDataFrame=True)
                    Lhand_data = self.import_hands(subj,trial,holes,'left')
                    Rhand_data = self.import_hands(subj,trial,holes,'right')

                    touched_spheres = general_data['TouchedSpheres']

                    for spheres_list in touched_spheres:
                        spheres_list = spheres_list.split(',')



                        for sphere in spheres_list:

                            sphere_data = surface_data[f'Sphere{sphere}']

                            #for frame in sphere_data:

























