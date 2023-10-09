from trial import *
from features import *

class Surface(Trial, FeatureExtraction):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.objects = 1
        self.nr_spheres = len(self.InitialSpherePositions())
        self.scale = 0 # add scale
        self.size = 0 # add size
        self.position = 0 # add central position


    def ImportInitialPositions(self):

        self.method_step = 1
        print(self.method_step, ' ImportInitialPositions()')

        tree = ET.parse(r'C:\Users\Sara\Desktop\DesignMotorTask\Data\initial_positions')
            #(r'/Users/smonteiro/Desktop/DesignMotorTask/Data/initial_positions.xml')
        root = tree.getroot()

        return (root)


    def ImportSpheres(self, subj=None):

        SubjectWarning(self, subj)

        if subj in self.subjects:

            self.method_step = 1
            print(self.method_step, ' ImportSpheres() subject: ', int(subj))

            tree = ET.parse(r"C:\Users\Sara\Desktop\DesignMotorTask\Data\subject_" + str(int(subj)) + "\\" + str(
                self.holes) + "_holes_1_flows_sphere_position_" + str(self.trial))

            #tree = ET.parse(r"/Users/smonteiro/Desktop/DesignMotorTask/Data/subject_" + str(int(subj))
            #                + "/" + str(self.holes) + "_holes_1_flows_sphere_position_" + str(self.trial) +".xml")
            root = tree.getroot()

            return (root)


    def InitialSpherePositions(self):
        """
        :return: initial sphere positions
        """

        data = self.ImportInitialPositions()
        initial_positions = pd.DataFrame()

        for sphere in np.arange(1, len(data)):

            sphere_position = np.zeros(3) #4

            for axis, position in zip(range(3), data[sphere][1]):
                sphere_position[axis] = position.text #axis+1

            new_row = pd.DataFrame([{"sphere_id": int(data[sphere][0].text),
                                     "x_position": sphere_position[0],
                                     "y_position": sphere_position[1],
                                     "z_position": sphere_position[2]}])
            initial_positions = pd.concat([initial_positions, new_row], ignore_index=True)

        self.method_step += 1
        print(self.method_step, ' InitialSpherePositions()')

        return initial_positions


    def PerFrameSpherePositions(self):
        """
        Here, stage and timeframe can be assigned/unassigned.
            if timeframe unassigned: timeframe == last frame of stage range
            if stage unassigned: stage == 'all'
            if both assigned: timeframe wins over last frame of stage range
        :return: sphere positions at trial stage/timeframe
        """

        sphere_dataframe = pd.DataFrame()

        for subj in self.subjects:

            sphere_data = self.ImportSpheres(subj=subj)
            general_data = self.ImportGeneral(subj=subj)
            frame_range = GetFrameRange(self.stage, len(general_data))[-1]

            if self.timeframe == None:
                timeframe = frame_range
            else:
                timeframe = self.timeframe

            if timeframe == -1 or timeframe == frame_range:
                frame = frame_range
            elif timeframe < frame_range and timeframe >= 0:
                frame = timeframe

            for sphere in np.arange(0,2*self.nr_spheres,2): # there are 145 spheres but data was duplicated, hence the 290

                sphere_info = sphere_data[timeframe][sphere]
                sphere_id, correct_id = SphereID(sphere_info)
                timestamp = float(general_data[frame][-3].text)
                frame_position = np.zeros(3)

                for axis, position in zip(range(3), sphere_info):
                    frame_position[axis] = float(position.text)

                new_row = pd.DataFrame([{"sphere_id": correct_id,
                                         "x_position": frame_position[0], #this had sphere_id
                                         "y_position": frame_position[1],
                                         "z_position": frame_position[2],
                                         "timestamp": timestamp}])

                sphere_dataframe = pd.concat([sphere_dataframe, new_row], ignore_index=True)

        self.method_step += 1
        print(self.method_step, ' PerFrameSpherePositions()')

        return sphere_dataframe.sort_values(by=['sphere_id']), frame_range


    def AvgSpherePositions(self):
        """
        Here, stage and timeframe can be assigned/unassigned.
            if timeframe unassigned: timeframe == last frame of stage range
            if stage unassigned: stage == 'all'
            if both assigned: timeframe wins over last frame of stage range
        :return: average sphere positions at trial stage/timeframe;
        variance; frame range
        """

        frame_position, frame_range = self.PerFrameSpherePositions()
        subject_trial = np.arange(0, len(frame_position), self.nr_spheres)
        # mean trial position of all spheres
        sphere_position = pd.DataFrame()
        var = np.zeros([self.nr_spheres,1])
        # number of spheres divided by nr of subjects
        for sphere in range( int(len(frame_position)/ self.nr_subjects)):
            avg_position = np.zeros([self.nr_subjects, 3])
            # iterate over all trials for the same sphere
            for i, subj in zip(range(len(subject_trial)), subject_trial):

                sphere_id = frame_position['sphere_id'][subj]
                position = np.array([frame_position['x_position'][subj],
                                     frame_position['y_position'][subj],
                                     frame_position['z_position'][subj]])
                # x,y,z individual sphere position of each subject trial
                avg_position[i] = position

            # compute variability of avg_position (has nr_subjects 3d arrays)
            # plot color gradient according to more or less variability
            var[sphere] = np.mean(np.array([np.var(avg_position[:,0]),
                                            np.var(avg_position[:,1]),
                                            np.var(avg_position[:,2])]))
            # compute mean across all trials
            new_row = pd.DataFrame([{"sphere_id": int(sphere_id),
                                     "x_position": np.mean(avg_position[:, 0]),
                                     "y_position": np.mean(avg_position[:, 1]),
                                     "z_position": np.mean(avg_position[:, 2])}])
            sphere_position = pd.concat([sphere_position, new_row], ignore_index=True)

            subject_trial += 1

        self.method_step += 1
        print(self.method_step, ' AvgSpherePositions()')

        return sphere_position, var, frame_range


    def MeshData(self, color_gradient_type=False):
        '''
        Here, stage and timeframe can be assigned/unassigned.
            if timeframe unassigned: timeframe == last frame of stage range
            if stage unassigned: stage == 'all'
            if both assigned: timeframe wins over last frame of stage range
        :param color_gradient_type: str; 'number' or 'duration' of touches
        :return: mesh data: x,y,z 1D arrays with sphere's coordinates;
                            corrected simplices;
                            1D array of color gradient values
        '''

        # if timeframe assigned AND < 5
        if self.timeframe != None and self.timeframe < 5:
            avg_position = self.InitialSpherePositions()
            var = np.zeros(len(avg_position))
        # if timeframe/stage assigned/unassigned
        else:
            avg_position, var, frame_range = self.AvgSpherePositions()

        sphere_id = avg_position['sphere_id']
        x = avg_position['x_position']
        y = avg_position['y_position']
        z = -avg_position['z_position']

        points = np.stack((x, z), axis=1)
        tri = Delaunay(points)
        simplices = []
        color_func = []

        for t, a, b, c in zip(tri.simplices, tri.simplices[:, 0], tri.simplices[:, 1], tri.simplices[:, 2]):

            if color_gradient_type == 'variance':
                d = float(var[a])
            else:
                d = 0

            simplices.append(list(t))
            color_func.append(d)

            d1 = np.abs(points[a][0] - points[b][0])
            d2 = np.abs(points[a][0] - points[c][0])
            d3 = np.abs(points[c][0] - points[b][0])
            d4 = np.abs(points[a][1] - points[b][1])
            d5 = np.abs(points[a][1] - points[c][1])
            d6 = np.abs(points[c][1] - points[b][1])

            if d1 > 0.06 or d2 > 0.06 or d3 > 0.06 or d4 > 0.06 or d5 > 0.06 or d6 > 0.06:
                simplices.remove(list(t))
                color_func.remove(d)

        self.method_step += 1
        print(self.method_step, ' MeshData()')

        return x, y, z, simplices, color_func


    def SurfaceMoving(self):
        """
            Is the surface moving. In which trial time is it moving. In which frames is it moving.
            What are the positions of each sphere.
            :return: The function has two returns.

                [0] object array of len(number of subjects) with:
                    a.  bool np.array: True if surface is moving, for each frame;
                        float np.array: timestamps of the trial;
                    b.  float np.array: timestamp where surface is moving;
                    c.  int np.array: frames where surface is moving.
                [1] DataFrame of moving positions for every sphere in the surface from all subjects in subjects.
            """

        initial_positions = self.InitialSpherePositions()
        is_surface_moving = np.zeros((self.nr_subjects, 3), dtype=object)
        moving_positions = pd.DataFrame()

        for s,subj in enumerate(self.subjects):

            sphere_data = self.ImportSpheres(subj=subj)
            frames = GetFrameRange(self.stage, len(sphere_data))
            prev_frame_position = np.zeros((3, self.nr_spheres))
            moving_timestamps = []
            moving_frames = []
            all_timestamps = np.zeros(len(frames))
            surface_moving = np.full(len(frames), False, dtype=bool)
            # first last positions is initial spheres positions
            last_positions = initial_positions

            for f, frame in enumerate(frames):
                frame_position = np.zeros((3, self.nr_spheres))
                timestamp = float(sphere_data[frame][-2].text)

                # nr_sphere * 2 (aug23, duplicated data mistake)
                for sphere in np.arange(0,2*self.nr_spheres,2):
                    # fix sphere id (apply to aug23 data, it has duplicated sphere data)
                    sphere_info = sphere_data[frame][sphere]
                    sphere_id, correct_id = SphereID(sphere_info)

                    for axis, position in zip(range(3), sphere_info):
                        # i/2 because of dup. data mistake
                        frame_position[:, int(sphere/2)][axis] = float(position.text)

                    ### THRESHOLD ###
                    # add positions of each sphere if they were different than last frame's position (means they were moving)
                    # if (frame_position[:,int(i/2)] != sphere_dict[correct_id][-1]).all():
                    # maybe just add if the movement was bigger than ...
                    # What is the optimal threshold?
                    if np.linalg.norm(frame_position[:, int(sphere/2)] -
                                      last_positions.iloc[int(sphere/2)][['x_position', 'y_position', 'z_position']]) > 0.02:

                        # update last position, to check if next frame moved compared to it
                        last_positions.loc[int(sphere/2), ['x_position', 'y_position', 'z_position']] = frame_position[:,int(sphere/2)]

                        new_row = pd.DataFrame([{"sphere_id": correct_id,
                                                 "x_position": frame_position[:,int(sphere/2)][0],
                                                 "y_position": frame_position[:,int(sphere/2)][1],
                                                 "z_position": frame_position[:,int(sphere/2)][2],
                                                 "timestamp": timestamp}])
                        moving_positions = pd.concat([moving_positions, new_row], ignore_index=True)

                # is surface moving #
                # (we remove first frame because prev_frame_position is zero)
                if frame != 0 and not np.array_equal(np.round(frame_position,5), np.round(prev_frame_position,5)):

                    moving_timestamps.append(timestamp)
                    moving_frames.append(frame)
                    surface_moving[f] = True

                all_timestamps[f] = timestamp
                prev_frame_position = frame_position

            is_surface_moving[s] = np.array([np.vstack((surface_moving, all_timestamps)),
                                             moving_timestamps,
                                             moving_frames], dtype=object)

        self.method_step += 1
        print(self.method_step, ' SurfaceMoving()')

        return is_surface_moving, moving_positions


    def TouchNumber(self):

        sphere_id = self.SurfaceMoving()[1]['sphere_id']
        initial_positions = self.InitialSpherePositions()

        initial_positions_touch = pd.DataFrame()

        for id in sphere_id:

            if id not in initial_positions_touch.values:

                new_row = pd.DataFrame([{"sphere_id": id,
                                         "x_position": float(initial_positions.loc[initial_positions['sphere_id'] == id]['x_position']),
                                         "y_position": float(initial_positions.loc[initial_positions['sphere_id'] == id]['y_position']),
                                         "z_position": float(initial_positions.loc[initial_positions['sphere_id'] == id]['z_position'])}])
                # list(sphere_id).count(id) == how many times sphere_id == id moved
                for i in range(list(sphere_id).count(id)):
                    initial_positions_touch = pd.concat([initial_positions_touch, new_row], ignore_index=True)

        self.method_step += 1
        print(self.method_step, ' TouchNumber()')

        return initial_positions_touch


    ### Density of hand touches per hand and for both hands ###
    def TouchDensity(self, surface=False, touch_number=False):

        if surface:

            moving_positions = self.SurfaceMoving()[1]
            x,y,z = moving_positions['x_position'], moving_positions['y_position'], moving_positions['z_position']

            KDE, xKDE, zKDE, values = GaussianKDE(x, z)
            surface = np.array([KDE, xKDE, zKDE, values], dtype=object)

            self.method_step += 1
            print(self.method_step, ' TouchDensity()')

            return surface, self.labels

        elif touch_number:

            touch_number = self.TouchNumber()
            x,y,z = touch_number['x_position'], touch_number['y_position'], touch_number['z_position']

            KDE, xKDE, zKDE, values = GaussianKDE(x, z)
            surface_over_initial = np.array([KDE, xKDE, zKDE, values], dtype=object)

            self.method_step += 1
            print(self.method_step, ' TouchDensity()')

            return surface_over_initial, self.labels

        else:
            print("TypeError: TouchDensity() missing 1 required positional argument: 'surface' or 'touch_number'.")



    ### Has all the sections and IDs ###
    def SurfaceSection(self, sphere_id_list=None, section_list=None, plot=False):

        spheres = self.InitialSpherePositions()
        initial_positions = spheres[1].T[1:].T
        sphere_id = spheres[1].T[0].T

        sections = self.section_list[np.arange(0,len(self.section_list),2)]

        norm_positions = MinMaxScaler(initial_positions)

        id_to_section = {}; section_to_id = {}

        for i, id in enumerate(sphere_id):
            id_to_section[int(id)] = []

        # create a self.surface_limits ... and substitute this section for a whole loop for each limit
        for i, id in enumerate(sphere_id):
            # for limit in sphere limits...:
            # for section in section list: .......
            # sphere_limits = {'LEdge': 0.3, .....}
            if norm_positions[0][i] < 0.3:
                id_to_section[int(id)].append('LEdge')
            if norm_positions[0][i] > 0.7:
                id_to_section[int(id)].append('REdge')
            if norm_positions[0][i] > 0.2 and norm_positions[0][i] < 0.8 and norm_positions[2][i] < 0.5:
                id_to_section[int(id)].append('CenterFront')
            if norm_positions[2][i] > 0.7:
                id_to_section[int(id)].append('Back')
            if norm_positions[0][i] < 0.5 and norm_positions[2][i] < 0.5:
                id_to_section[int(id)].append('LCorner')
            if norm_positions[0][i] > 0.5 and norm_positions[2][i] < 0.5:
                id_to_section[int(id)].append('RCorner')
            if norm_positions[0][i] > 0.3 and norm_positions[0][i] < 0.7 and \
                    norm_positions[2][i] > 0.3 and norm_positions[2][i] < 0.7:
                id_to_section[int(id)].append('Center')
            if norm_positions[0][i] < 0.05:
                id_to_section[int(id)].append('LLimit')
            if norm_positions[0][i] > 0.95:
                id_to_section[int(id)].append('RLimit')
            if norm_positions[2][i] > 0.95:
                id_to_section[int(id)].append('BackLimit')
            if norm_positions[2][i] < 0.05:
                id_to_section[int(id)].append('FrontLimit')

        section_to_id['LEdge'] = [k for k, v in id_to_section.items() if 'LEdge' in v]
        section_to_id['REdge'] = [k for k, v in id_to_section.items() if 'REdge' in v]
        section_to_id['CenterFront'] = [k for k, v in id_to_section.items() if 'CenterFront' in v]
        section_to_id['Back'] = [k for k, v in id_to_section.items() if 'Back' in v]
        section_to_id['LCorner'] = [k for k, v in id_to_section.items() if 'LCorner' in v]
        section_to_id['RCorner'] = [k for k, v in id_to_section.items() if 'RCorner' in v]
        section_to_id['Center'] = [k for k, v in id_to_section.items() if 'Center' in v]
        section_to_id['LLimit'] = [k for k, v in id_to_section.items() if 'LLimit' in v]
        section_to_id['RLimit'] = [k for k, v in id_to_section.items() if 'RLimit' in v]
        section_to_id['BackLimit'] = [k for k, v in id_to_section.items() if 'BackLimit' in v]
        section_to_id['FrontLimit'] = [k for k, v in id_to_section.items() if 'FrontLimit' in v]

        # add plot section to plots function....

        return id_to_section, section_to_id