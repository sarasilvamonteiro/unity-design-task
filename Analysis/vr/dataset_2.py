import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
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


    def __init__(self, IOS=False, Windows=False):

        # i should create a file that saves the good subjects and the path of the data
        # the number of spheres and the number of hand joints

        self.IOS = IOS
        self.Windows = Windows
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
        print(f'Importing general data...')
        if self.IOS:
            tree = ET.parse("" + self.path + "/subject_" + str(int(subj))
                            + "/" + str(holes) + "_holes_1_flows_general_" + str(trial))
        if self.Windows:
            tree = ET.parse(self.path + "\subject_" + str(int(subj))
                            + "\\" + str(holes) + "_holes_1_flows_general_" + str(trial))
        root = tree.getroot()

        if toDataFrame:
            return self.XMLtoDataFrame(root)
        else:
            return root
    def import_hands(self, subj, trial, holes, hand, toDataFrame = False):
        print(f'Importing {hand.lower()} hand data...')
        if self.IOS:
            tree = ET.parse(r"" + self.path + "/subject_" + str(int(subj)) + "/" +
                             str(holes) + "_holes_1_flows_" + str(hand) + "_hand_" + str(trial))
        if self.Windows:
            tree = ET.parse(self.path + "\subject_" + str(int(subj))
                            + "\\" + str(holes) + "_holes_1_flows_" + str(hand) + "_hand_" + str(trial))
        root = tree.getroot()

        if toDataFrame:
            return self.XMLtoDataFrame(root)
        else:
            return root
    def import_surface(self, subj=None, trial=None, holes=None, frame=slice(None), toDataFrame=False):
        print(f'Importing surface data...')
        # this is just if we want to import initial positions
        if subj == None:
            subj = self.subjects[0]
            holes = 1
            trial = 1
            frame = 0

        if self.IOS:
            tree = ET.parse(r"" + self.path + "/subject_" + str(int(subj))
                            + "/" + str(holes) + "_holes_1_flows_surface_" + str(trial))
        if self.Windows:
            tree = ET.parse(self.path + "\subject_" + str(int(subj)) + "\\" +
                            str(holes) + "_holes_1_flows_surface_" + str(trial))
        root = tree.getroot()

        if toDataFrame:
            return self.XMLtoDataFrame(root)
        else:
            return root[frame]

    def import_fluid(self, subj, trial, holes, toDataFrame=False):
        print(f'Importing fluid data...')
        if self.IOS:
            tree = ET.parse(r"" + self.path + "/subject_" + str(int(subj))
                            + "/" + str(holes) + "_holes_1_flows_fluid_" + str(trial))
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
                #print(f'Reading {element.tag}...')
                # if column doesn't have nested values:
                if len(element) == 0:
                    row_data[element.tag] = element.text
                # check if column has nested values (e.g. x,y,z)
                else:
                    row_data_1 = {}
                    for axis in element:
                        row_data_1[axis.tag] = axis.text
                    row_data[element.tag] = row_data_1

                if element.tag not in df_columns:
                    df_columns.append(element.tag)
            df_data.append(row_data)
        # Pandas DataFrame
        df = pd.DataFrame(df_data, columns=df_columns)

        # do something like this if you want to keep a dataframe
        # inside the main columns (not recommended, takes longer)
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
        Load data and check when hands are touching the surface.
        Create a Dataframe with the frames where those deformations occur,
        labeled as individual syllables.
        Save the resulting Dataframe.
        """

        surface_syllables_df = pd.DataFrame()
        hand_syllables_df = pd.DataFrame()
        eye_syllables_df = pd.DataFrame()
        touched_spheres_df = pd.DataFrame()

        def save_to_syllable_df(object_df, object_data, hand, transpose=True):
            """
            Select columns with position and time information.
            Add columns with complementary information.
            :param object_data: imported data (either from hand or surface)
            :param object_df: Dataframe where syllable information is being saved.
            :param hand: Which hand is being used.
            :return: Resulting new row.
            """

            # current frame, first columns (position), last column (time)
            new_syllable = pd.DataFrame(object_data)
            if transpose:
                new_syllable = new_syllable.T
            # complementary information columns
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
                print(f'Getting syllables for subject {subj}, trial {trial}, holes {holes}:')
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
                # get touched spheres
                L_touched_spheres = general_data['SphereID_LTouch']
                R_touched_spheres = general_data['SphereID_RTouch']
                # initialize syllable count
                syllable = 0
                last_syllable = syllable

                print('Generating syllables...')
                # save data when deformation occurs
                for frame in range(len(general_data)):
                    touch = False
                    #print(syllable, frame)
                    # get two frames before and two frames after deformation
                    # check if frame is in deformation indexes
                    if any([f in L_touch for f in np.arange(frame-1, frame+2, 1)]):
                        ### save surface syllables ###
                        surface_syllables_df = save_to_syllable_df(surface_syllables_df,
                                                                   surface_data.iloc[frame,
                                                                   list(range(surface_data.shape[1]-3)) +
                                                                   [surface_data.shape[1]-1]], hand='Left')
                        ### save hand syllables ###
                        hand_syllables_df = save_to_syllable_df(hand_syllables_df,
                                                                Lhand_data.iloc[frame, list(range(Lhand_data.shape[1]-3)) +
                                                                [Lhand_data.shape[1]-1]], hand='Left')
                        ### save eye syllables ###
                        eye_syllables_df = save_to_syllable_df(eye_syllables_df,
                                                               general_data.iloc[frame, [1] +
                                                               [general_data.shape[1]-1]], hand='Left')
                        # update last_syllable
                        last_syllable = syllable
                        touch = True

                    if any([f in R_touch for f in np.arange(frame-1, frame+2, 1)]):
                        ### save surface syllables ###
                        surface_syllables_df = save_to_syllable_df(surface_syllables_df,
                                                                   surface_data.iloc[frame,
                                                                   list(range(surface_data.shape[1]-3)) +
                                                                   [surface_data.shape[1]-1]], hand='Right')
                        ### save hand syllables ###
                        hand_syllables_df = save_to_syllable_df(hand_syllables_df,
                                                                Rhand_data.iloc[frame, list(range(Rhand_data.shape[1]-3)) +
                                                                [Rhand_data.shape[1]-1]], hand='Right')
                        ### save eye syllables ###
                        eye_syllables_df = save_to_syllable_df(eye_syllables_df,
                                                               general_data.iloc[frame, [1] +
                                                               [general_data.shape[1]-1]], hand='Right')
                        # update last_syllable
                        last_syllable = syllable
                        touch = True

                    ### save touched spheres ###
                    if L_touched_spheres.iloc[frame] != None:
                        spheres_list = L_touched_spheres.iloc[frame].split(',')
                        for sphere in spheres_list:
                            touched_spheres_df = save_to_syllable_df(touched_spheres_df,
                                                                     [{'SphereID': sphere,
                                                                       'Timestamp': general_data['Timestamp'][frame]}],
                                                                     hand='Left', transpose=False)
                    if R_touched_spheres.iloc[frame] != None:
                        spheres_list = R_touched_spheres.iloc[frame].split(',')
                        for sphere in spheres_list:
                            touched_spheres_df = save_to_syllable_df(touched_spheres_df,
                                                                     [{'SphereID': sphere,
                                                                       'Timestamp': general_data['Timestamp'][frame]}],
                                                                     hand='Right', transpose=False)
                    if not touch:
                        touch = False
                        syllable = last_syllable + 1

        # save syllables
        surface_syllables_df.set_index(['syllable','subject','trial', 'holes', 'level_order', 'hand']).to_pickle('surface_syllables')
        hand_syllables_df.set_index(['syllable','subject','trial', 'holes', 'level_order', 'hand']).to_pickle('hand_syllables')
        eye_syllables_df.set_index(['syllable', 'subject', 'trial', 'holes', 'level_order', 'hand']).to_pickle('eye_syllables')
        touched_spheres_df.set_index(['syllable', 'subject', 'trial', 'holes', 'level_order', 'hand']).to_pickle('sphereID_syllables')
        print('Done.')
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
        print('Preprocessing...')

        if 'PalmPosition' in data.columns:
            object = 'hands'
            print(object)
        if 'Sphere2000' in data.columns:
            object = 'surface'
            print(object)
        if 'AgentLookingAt' in data.columns:
            object = 'eye'
            print(object)

        # we need to copy the original data so that it doesn't change the original
        #preprocessed_data = copy.deepcopy(data)
        # new dataframe
        preprocessed_data = pd.DataFrame(columns=data.columns)#, index=data.index.names)
        # get syllables index
        syllables = np.unique(data.index.get_level_values('syllable'))
        multi_indices =  np.unique(data.index)
        indices_data = pd.DataFrame()

        # iterate over each different syllable
        # when we select one syllable we get all the timeframes of that deformation
        # what we want is to normalize/upsample them
        for syllable in syllables:
            for hand in np.unique(data.loc[syllable].index.get_level_values('hand')):

                idx = list(preprocessed_data.index)
                new_rows = list(map(str, range(len(preprocessed_data),
                                               len(preprocessed_data) + length)))
                idx.extend(new_rows)
                preprocessed_data = preprocessed_data.reindex(index=idx)
                indices_data = indices_data.reindex(index=idx)

                columns_dict = {'syllable': syllable, 'subject': multi_indices[0][1], 'trial': multi_indices[0][2],
                                'holes': multi_indices[0][3], 'level_order': multi_indices[0][4], 'hand': hand}
                for col_name, col_value in columns_dict.items():
                    indices_data.loc[new_rows,col_name] = col_value

                indices_data = indices_data.astype({i:int for i in indices_data.columns[:-1]})

                # get joint/sphere info (column)
                for column in data.columns:
                    # array of current lenght
                    sample_length = np.arange(0, len(data.loc[syllable, :, :, :, :, hand]), 1)
                    # array of resampled length
                    new_length = np.arange(0, len(data.loc[syllable, :, :, :, :, hand]) - 1,
                                           (len(data.loc[syllable, :, :, :, :, hand]) - 1) / length)[:length]
                    # apply interpolation over each axis (x,y,z)
                    # upsample joint/sphere positions (0 to length for each axis)
                    if column != 'Timestamp':
                        positions = {}
                        for axis in ['x', 'y', 'z']:
                            if resample:
                                interpolator = interp1d(sample_length,
                                                    data.loc[syllable, :, :, :, :, hand][column].apply(lambda x: x[axis]),
                                                    kind=kind)(new_length)
                            if norm_position:
                                interpolator = normalizer.fit_transform(interpolator.reshape(-1, 1))
                            positions[axis] = interpolator
                        upsampled_syllable = [{'x':float(x), 'y': float(y), 'z': float(z)}
                                              for x,y,z in zip(positions['x'],positions['y'],positions['z'])]
                    # upsample Timestamps (0 to length)
                    if column == 'Timestamp':
                        if resample:
                            interpolator = interp1d(sample_length,
                                                data.loc[syllable, :, :, :, :, hand][column],
                                                kind=kind)(new_length)
                        if norm_time:
                            interpolator = normalizer.fit_transform(interpolator.reshape(-1, 1))
                        upsampled_syllable = interpolator

                    # save upsampled column in new dataframe
                    preprocessed_data.loc[new_rows, column] = np.array(upsampled_syllable).flatten()

        # add indices and save
        preprocessed_data = pd.concat([indices_data, preprocessed_data], axis=1)
        preprocessed_data = preprocessed_data.set_index(['syllable','subject','trial', 'holes', 'level_order', 'hand'])
        preprocessed_data.to_pickle(str(object) + '_preprocessed_syllables')
        print('Done.')
        return preprocessed_data

    def extract_values(self, data, as_array=False):
        """
        Get x,y,z,time as features (each column has one element).
        T: number of timestamps
        Number of columns: number of joints/spheres/eyes * number of axis (x,y,z) * T + T
        The last T columns are the timestamps.
        :param data: data to transform (raw or preprocessed).
        :param as_array: bool
        """
        print('Extracting values as features...')
        values = pd.DataFrame(columns=np.unique(data.index))

        for syllable, subj, trial, holes, level_order, hand in np.unique(data.index):
            features = data.loc[syllable, subj, trial, holes, level_order, hand]['Timestamp'].values.reshape(-1, 1).T
            for column in data.columns[:-1]:
                features = np.concatenate((data.loc[syllable, subj, trial,
                holes, level_order, hand][column].apply(pd.Series).values.reshape(-1, 1).T, features), axis=1)
            values[(syllable, subj, trial, holes, level_order, hand)] = features.flatten()
        print('Done.')
        return values.T



    # check hand and surface labels
    # i can just load normally spheres and check if hand is touching it....
    # i can just load hands and check if is touching a sphere....
























