from auxiliary import *
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
from scipy.spatial import Delaunay

#class Task():

    #def __init__(self):

     #   self.total_subjects = 10
     #   self.total_trials = 1000



class Trial():

    def __init__(self, trial, holes, when_was_shown, subject=None, stage=None, timeframe=None):
        """
        :param trial: trial number
        :param holes: number of holes in trial
        :param when_was_shown: subject group this trial was show to
        :param subject: subject to get trial info from
        :param stage: trial stage to get positions
        :param timeframe: trial timeframe to get positions
        """

        # when we access Trial(subjects=None) from Surface(subjects=trial.subjects), trial.subjects is not None
        # anymore, because it was defined previously in Trial() as a list of all the subjects.
        if type(subject) == int:
            self.subjects = np.arange(subject, subject+1, 1)
        # if subjects is not assigned we define it as a list of all the subjects
        elif type(subject) == type(None):
            self.subjects = GetSubjects(holes, when_was_shown)
        else:
            self.subjects = subject

        self.trial = trial
        self.holes = holes
        self.when_was_shown = when_was_shown
        self.nr_subjects = len(self.subjects)
        self.stage = stage
        self.timeframe = timeframe
        self.nr_trials = 7
        self.method_step = 0
        self.labels = [trial, holes, when_was_shown, stage]


    def ImportGeneral(self, subj=None):
        """
        :param subj: int, subject to import trial info from
        :return: general trial data
        """

        if self.nr_subjects == 1:
            subj = self.subjects
        if subj == None:
            print("TypeError: ImportGeneral() missing 1 required positional argument: 'subj'")
        if subj not in self.subjects:
            print("TypeError: 'subj' must belong to 'subjects'")

        if subj in self.subjects:

            #info = np.load(get info file and check how many trials)
            #self.nr_trials = ....

            self.method_step = 1
            print(self.method_step, ' ImportGeneral() subject: ', int(subj))

            #'C:/Users/teaching lab/Desktop/
            tree = ET.parse(r'/Users/smonteiro/Desktop/DesignMotorTask/Data/subject_' + str(int(subj))
                            + "/" + str(self.holes) + "_holes_1_flows_general_" + str(self.trial) + ".xml")
            root = tree.getroot()

            return (root)



class Surface(Trial):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nr_spheres = len(self.InitialSpherePositions())
        self.scale = 0 # add scale
        self.size = 0 # add size
        self.position = 0 # add central position


    def ImportInitialPositions(self):

        self.method_step = 1
        print(self.method_step, ' ImportInitialPositions()')

        tree = ET.parse(r'/Users/smonteiro/Desktop/DesignMotorTask/Data/initial_positions.xml')
        root = tree.getroot()

        return (root)


    def ImportSpheres(self, subj=None):

        if self.nr_subjects == 1:
            subj = self.subjects
        if subj == None:
            print("TypeError: ImportSpheres() missing 1 required positional argument: 'subj'")
        if subj not in self.subjects:
            print("TypeError: 'subj' must belong to 'subjects'")

        if subj in self.subjects:

            self.method_step = 1
            print(self.method_step, ' ImportSpheres() subject: ', int(subj))

            tree = ET.parse(r"/Users/smonteiro/Desktop/DesignMotorTask/Data/subject_" + str(int(subj))
                            + "/" + str(self.holes) + "_holes_1_flows_sphere_position_" + str(self.trial) +".xml")
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



class Hands(Trial):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def ImportHands(self, hand, subj=None):

        if self.nr_subjects == 1:
            subj = self.subjects
        if subj == None:
            print("TypeError: ImportHands() missing 1 required positional argument: 'subj'")
        if subj not in self.subjects:
            print("TypeError: 'subj' must belong to 'subjects'")

        if subj in self.subjects:

            self.method_step = 1
            print(self.method_step, " ImportHands('" + str(hand)+ "') subject: ", int(subj))

            tree = ET.parse(r"/Users/smonteiro/Desktop/DesignMotorTask/Data/subject_" + str(int(subj))
                            + "/" + str(self.holes) + "_holes_1_flows_" + str(hand) + "_hand_data_" + str(self.trial)+".xml")
            root = tree.getroot()

            return (root)


    def HandPositions(self, touch=True, hand=True):
        """
        :param touch: bool. True, hand positions when touching the surface; False, all hand positions.
        :param hand: bool, str. True, 'both'; 'left'; 'right'.
        :return: right and left hand positions and timeframes.
        """

        is_surface_moving = Surface(self.trial, self.holes, self.when_was_shown,
                                    self.subjects, self.stage, self.timeframe).SurfaceMoving()[0]

        rhand_dataframe = pd.DataFrame()
        lhand_dataframe = pd.DataFrame()

        def SaveToDataFrame(hand_dataframe, palm, hand_id):

            palm_frame_position = np.zeros(3)

            for axis, position in zip(range(3), palm):
                palm_frame_position[axis] = float(position.text)

            # -2 for left, -1 for right
            if general_data[frame][-(hand_id + 1)].text == 'true':

                new_row = pd.DataFrame([{"x_position": palm_frame_position[0],
                                         "y_position": palm_frame_position[1],
                                         "z_position": palm_frame_position[2],
                                         "timestamp": timestamp}])
                hand_dataframe = pd.concat([hand_dataframe, new_row], ignore_index=True)

            return hand_dataframe

        for s, subj in enumerate(self.subjects):

            general_data = self.ImportGeneral(subj=subj)
            frames = GetFrameRange(self.stage, len(general_data))

            print(self.method_step, ' Frame range: ',frames[-1])

            rhand_data = self.ImportHands(subj=subj, hand="right")
            lhand_data = self.ImportHands(subj=subj, hand="left")

            for f, frame in enumerate(frames):

                timestamp = float(general_data[frame][-3].text)
                touching = is_surface_moving[s][0][0][f]

                lpalm = lhand_data[frame][0]
                rpalm = rhand_data[frame][0]

                if touch and bool(touching) == True:
                    if hand == True or hand == 'both' or hand == 'right':
                        rhand_dataframe = SaveToDataFrame(rhand_dataframe, rpalm, 0)
                    if hand == True or hand == 'both' or hand == 'left':
                        lhand_dataframe = SaveToDataFrame(lhand_dataframe, lpalm, 1)
                if not touch:
                    if hand == True or hand == 'both' or hand == 'right':
                        rhand_dataframe = SaveToDataFrame(rhand_dataframe, rpalm, 0)
                    if hand == True or hand == 'both' or hand == 'left':
                        lhand_dataframe = SaveToDataFrame(lhand_dataframe, lpalm, 1)

            self.method_step += 1
            print(self.method_step, ' HandPositions()')

        return rhand_dataframe, lhand_dataframe


    ### Density of hand touches per hand and for both hands ###
    def TouchDensity(self, hand=True):
        """
        :param hand: bool, str. True, 'both'; 'left'; 'right'.
        :return: right, left, and both Gaussian KDE results; labels
        """

        rtouch_data, ltouch_data = self.HandPositions(hand=hand)
        lx,ly,lz = [[],[],[]]; rx,ry,rz = [[],[],[]]
        left = np.zeros(4); right = np.zeros(4); both = np.zeros(4)

        print(self.method_step, ' R ', len(rtouch_data))
        print(self.method_step, ' L ', len(ltouch_data))

        if len(ltouch_data) > 1:
            lx = ltouch_data['x_position']; ly = ltouch_data['y_position']; lz = ltouch_data['z_position']
            if hand == 'both':
                KDE, xKDE, zKDE, values = GaussianKDE(np.append(lx, rx), np.append(lz, rz))
                both = np.array([KDE, xKDE, zKDE, values], dtype=object)
            if hand == 'left' or hand == True:
                KDE, xKDE, zKDE, values = GaussianKDE(lx, lz)
                left = np.array([KDE, xKDE, zKDE, values], dtype=object)

        if len(rtouch_data) > 1:
            rx = rtouch_data['x_position']; ry = rtouch_data['y_position']; rz = rtouch_data['z_position']
            if hand == 'both':
                KDE, xKDE, zKDE, values = GaussianKDE(np.append(lx, rx), np.append(lz, rz))
                both = np.array([KDE, xKDE, zKDE, values], dtype=object)
            if hand == 'right' or hand == True:
                KDE, xKDE, zKDE, values = GaussianKDE(rx, rz)
                right = np.array([KDE, xKDE, zKDE, values], dtype=object)

        self.method_step += 1
        print(self.method_step, ' TouchDensity()')

        return right, left, both, self.labels



class Fluid(Trial):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    ### Get fluid count per hole ###
    def FluidCountPerHole(self):

        caught_array = np.zeros(self.nr_subjects, dtype=object)
        emitted_array = np.zeros(self.nr_subjects, dtype=object)

        for s, subj in enumerate(self.subjects):

            general_data = self.ImportGeneral(subj)
            subj_caught = np.zeros(len(general_data), dtype=object)
            subj_emitted = np.zeros(len(general_data), dtype=object)

            for frame in range(len(general_data)):
                count = np.zeros(self.holes, dtype=object)

                for hole, fluid in zip(range(self.holes), general_data[frame][-8]):
                    count[hole] = float(fluid.text)

                subj_caught[frame]= count
                subj_emitted[frame] = float(general_data[frame][-9].text)

            caught_array[s] = subj_caught
            emitted_array[s] = subj_emitted

        self.method_step += 1
        print(self.method_step, ' FluidCountPerHole()')# subject: ', int(subj))

        return caught_array, emitted_array


    ### Fluid score for each subject across time ###
    def Score(self):

        caught_all, emitted_all = self.FluidCountPerHole()
        frames = []
        score_all= []

        for subj in range(len(caught_all)):

            with_fluid_frames = 0
            score = []

            for caught, emitted in zip(caught_all[subj], emitted_all[subj]):

                if emitted > 0 :

                    with_fluid_frames += 1

                    if self.holes == 1:
                        score.append(caught/emitted)
                    if self.holes == 2:
                        score.append(np.array([2*np.min(caught/emitted)], dtype=object))

            frames.append(with_fluid_frames)
            score_all.append(score)

        # fix trials that ended earlier
        for subj in range(len(frames)):

            difference = np.max(frames) - frames[subj]

            for frame in range(difference):
                score_all[subj].append(score_all[subj][-1])

        self.method_step += 1
        print(self.method_step, ' Score()')

        return score_all


    #### Mean and Standard Dev for fluid over trials ###
    def MeanFluidScore(self):

        trial = self.trial
        mean_trials = np.zeros((self.nr_trials,300,1))

        for t in range(self.nr_trials):

            self.trial = t
            trial_score = self.Score()
            print(self.method_step, ' Trial: ', self.trial)
            mean_trials[t] = np.mean(np.array(trial_score), axis=0)[:300]

        std_trials = np.std(mean_trials, axis=0)

        self.trial = trial
        self.method_step += 1
        print(self.method_step, ' MeanFluidScore()')

        return mean_trials, std_trials



class Eyes(Trial):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # i think i can optimize this... we can add to the general data if surface is moving or not and which hand is touching it
    # Initial eye gaze before deformation ocurs #
    def InitialEyeGaze(self):

        initial_gaze = pd.DataFrame()
        surface_moving = Surface(self.trial, self.holes, self.when_was_shown,
                                 self.subjects, self.stage, self.timeframe).SurfaceMoving()

        for s, subj in enumerate(self.subjects):

            # get frames before moving:
            moving_frames = surface_moving[0][s][2]
            general_data = self.ImportGeneral(subj)

            for frame in range(len(general_data)):
                if frame < moving_frames[0]: # five frames tolerance before deformation starts?

                    timestamp = float(general_data[frame][-3].text)
                    frame_looking_at = np.zeros(3)

                    for axis, position in zip(range(3), general_data[frame][1]):
                        frame_looking_at[axis] = float(position.text)

                    new_row = pd.DataFrame([{"subject": subj,
                                             "x_position": frame_looking_at[0],
                                             "y_position": frame_looking_at[1],
                                             "z_position": frame_looking_at[2],
                                             "timestamp": timestamp}])
                    initial_gaze = pd.concat([initial_gaze, new_row], ignore_index=True)

        self.method_step += 1
        print(self.method_step, ' InitialEyeGaze()')

        return initial_gaze


    # Eye gaze per stage #
    def EyeGaze(self):

        looking_at = pd.DataFrame()

        for s, subj in enumerate(self.subjects):

            # get frames:
            general_data = self.ImportGeneral(subj)
            frames = GetFrameRange(self.stage, len(general_data))

            for f, frame in enumerate(frames):

                timestamp = float(general_data[frame][-3].text)
                frame_looking_at = np.zeros(3)

                for axis, position in zip(range(3), general_data[frame][1]):
                    frame_looking_at[axis] = float(position.text)

                new_row = pd.DataFrame([{"x_position": frame_looking_at[0],
                                         "y_position": frame_looking_at[1],
                                         "z_position": frame_looking_at[2],
                                         "timestamp": timestamp}])
                looking_at = pd.concat([looking_at, new_row], ignore_index=True)

        self.method_step += 1
        print(self.method_step, ' EyeGaze()')

        return looking_at






