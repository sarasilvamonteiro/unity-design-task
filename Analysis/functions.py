from import_data import *
from auxiliary import *
import numpy as np
import pandas as pd
from scipy.spatial import Delaunay


#####################################
############ SPHERE DATA ############
#####################################

### Initial sphere positions ###
def InitialSpherePositions():

    data = ImportInitialPositions()
    initial_positions = []
    dict_initial = {}

    for sphere in np.arange(1, len(data)):

        sphere_position = np.zeros(3) #4
        #sphere_position[0] = int(ImportInitialPositions()[sphere][0].text)
        for axis, position in zip(range(3), data[sphere][1]):

            sphere_position[axis] = position.text #axis+1

        initial_positions.append((int(data[sphere][0].text), sphere_position[0], sphere_position[1], sphere_position[2]))
        dict_initial[int(data[sphere][0].text)] = sphere_position

    return dict_initial, np.array(initial_positions)



### Sphere positions at timeframe ###
def PerFrameSpherePositions(trial, holes, when_was_shown, stage=None, timeframe=None):

    subjects = GetSubjects(holes, when_was_shown)
    nr_trials = len(subjects
                    )
    sphere_dataframe = pd.DataFrame()

    for subj in subjects:

        sphere_data = ImportSpheres(subj, trial, holes)
        general_data = ImportGeneral(subj, trial, holes)

        if stage != None:
            frame_range = GetFrameRange(stage, len(general_data))[-1]
            timeframe = frame_range
        else:
            frame_range = len(general_data)

        frame = frame_range
        print(frame_range)

        if timeframe == -1 or timeframe == frame_range:
            frame == frame_range

        elif timeframe < frame_range and timeframe >= 0:
            frame = timeframe

        for sphere in np.arange(0,290,2):

            sphere_position, sphere_id, correct_id = SphereID(sphere_data, sphere, frame)
            timestamp = float(general_data[frame][-3].text)
            frame_position = np.zeros(3)

            for axis, position in zip(range(3), sphere_position):
                frame_position[axis] = float(position.text)

            new_row = pd.DataFrame([{"sphere_id": sphere_id, "x_position": frame_position[0],
                                     "y_position": frame_position[1], "z_position": frame_position[2],
                                     "timestamp": timestamp}])

            sphere_dataframe = pd.concat([sphere_dataframe, new_row], ignore_index=True)

    return sphere_dataframe.sort_values(by=['sphere_id']), frame_range, nr_trials





### Average sphere positions at timeframe ###
def AvgSpherePositions(trial, holes, when_was_shown, stage=None, timeframe=None):

    frame_position, frame_range, nr_trials = PerFrameSpherePositions(trial, holes, when_was_shown, stage, timeframe)
    subject_trial = np.arange(0, len(frame_position), 145)
    sphere_position = np.zeros([145, 4]) # mean trial position of all spheres
    var = np.zeros([145,1])
    for sphere in range(int(len(frame_position) / nr_trials)):  # number of spheres divided by number of trials

        avg_position = np.zeros([nr_trials, 3])

        for i, trial in zip(range(len(subject_trial)), subject_trial):
            sphere_id = frame_position['sphere_id'][trial]
            position = np.array([frame_position['x_position'][trial], frame_position['y_position'][trial],
                                 frame_position['z_position'][trial]])
            avg_position[i] = position # x,y,z individual sphere position of each subject trial

        # compute variability of avg_position (has 5 3d arrays, one for each subject)
        # see which spheres have more variability and plot color gradient according to more or less variability

        var[sphere] = np.mean(np.array([np.var(avg_position[:,0]),np.var(avg_position[:,1]),np.var(avg_position[:,2])]))

        sphere_position[sphere] = np.array(
            [sphere_id, np.mean(avg_position[:, 0]), np.mean(avg_position[:, 1]), np.mean(avg_position[:, 2])]) # compute mean across all 5 trials

        subject_trial += 1

    return sphere_position, var, frame_range





### Sphere mesh data ###
def MeshData(subject=None, trial=None, holes=None, when_was_shown=None, stage=None, timeframe=None, color_gradient_type=False):

    '''
    :param trial: int; number of trial
    :param holes: int; number of holes
    :param when_was_shown: str; 'first' or 'last'
    :param timeframe: int
    :param color_gradient_type: str; 'number' or 'duration' of touches
    :return: 3 1D arrays with each sphere coordinates; corrected simplices; 1D array of gradient values
    '''

    if stage != None or (timeframe != -1 and timeframe > 5):
        avg_position, var, frame_range = AvgSpherePositions(trial, holes, when_was_shown, stage, timeframe)

    else:
        avg_position = InitialSpherePositions()[1]
        var = np.zeros(len(avg_position))

    sphere_id = avg_position[:, 0]
    x = avg_position[:, 1]
    y = avg_position[:, 2]
    z = -avg_position[:, 3]

    points = np.stack((z, x), axis=1)
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

    return z, x, y, simplices, color_func




#####################################
########## NEW: WITH HANDS ##########
#####################################

### Timestamps surface is moving ###
def SurfaceMoving(trial, holes, stage, subject=None, when_was_shown=None):

    print("subject:", subject)

    if subject != None:
        subjects = np.arange(subject, subject+1, 1)
    else:
        subjects = GetSubjects(holes, when_was_shown)


    is_surface_moving = np.zeros((len(subjects), 3), dtype=object)

    moving_positions = pd.DataFrame()
    #moving_positions = InitialSpherePositions()[0]
    #for key in moving_positions.keys():
    #    moving_positions[key] = list(np.array([moving_positions[key]]))

    for s,subj in zip(range(len(subjects)), subjects):

        sphere_data = ImportSpheres(subj, trial, holes)
        frames = GetFrameRange(stage, len(sphere_data))

        prev_frame_position = np.zeros((3, 145)) # sphere nr = 145
        moving_timestamps = []
        moving_frames = []
        all_timestamps = np.zeros(len(frames))
        surface_moving = np.full(len(frames), False, dtype=bool)

        sphere_dict = InitialSpherePositions()[0]
        for key in sphere_dict.keys():
            sphere_dict[key] = list(np.array([sphere_dict[key]]))
        # get initial spheres positions
        # if frame positions for each sphere is different than initial sphere position, save its position

        for f, frame in zip(range(len(frames)),frames):

            frame_position = np.zeros((3, 145))
            timestamp = float(sphere_data[frame][-2].text)

            for i in np.arange(0,290,2):

                sphere = sphere_data[frame][i]
                sphere_id = int(sphere.tag[-4:])
                correct_id = int(2000 + (sphere_id - 2000) /2) # fix sphere id (apply to aug23 data, it has duplicated sphere data)

                for axis, position in zip(range(3), sphere):
                    frame_position[:,int(i/2)][axis] = float(position.text)

                ### THRESHOLD ###
                # maybe just add if the movement was bigger than ...
                if np.linalg.norm(frame_position[:, int(i / 2)] - sphere_dict[correct_id][-1]) > 0.02: # What is the optimal threshold?
                # add positions of each sphere if they were different than last frame's position (means they were moving)
                #if (frame_position[:,int(i/2)] != sphere_dict[correct_id][-1]).all():
                    sphere_dict[correct_id].append(frame_position[:,int(i/2)])

                    new_row = pd.DataFrame([{"sphere_id": correct_id, "x_position": frame_position[:,int(i/2)][0],
                                         "y_position": frame_position[:,int(i/2)][1], "z_position": frame_position[:,int(i/2)][2],
                                         "timestamp": timestamp}])

                    moving_positions = pd.concat([moving_positions, new_row], ignore_index=True)
                    #moving_positions[correct_id].append(frame_position[:,int(i/2)])
                    # when plotting remove the first value as it is the initial sphere position

            # is surface moving #
            if frame != 0 and not np.array_equal(np.round(frame_position,5), np.round(prev_frame_position,5)):
                # (we remove first frame because prev_frame_position is zero)

                moving_timestamps.append(timestamp)
                moving_frames.append(frame)
                surface_moving[f] = True

            all_timestamps[f] = timestamp
            prev_frame_position = frame_position


        is_surface_moving[s] = np.array([np.vstack((surface_moving, all_timestamps)), moving_timestamps, moving_frames], dtype=object)
        #moving_positions[s] = sphere_dict

    return is_surface_moving, moving_positions




### Positions touched by each hand ###
def HandPositions(trial, holes, stage, subject=None, when_was_shown=None, touch=True, hand=True):

    if subject != None:
        subjects = np.arange(subject, subject+1,1)
    else:
        subjects = GetSubjects(holes, when_was_shown)

    is_surface_moving = SurfaceMoving(subject=subject, trial=trial, holes=holes, when_was_shown=when_was_shown, stage=stage)[0]

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

    for s, subj in zip(range(len(subjects)),subjects):

        general_data = ImportGeneral(subj, trial, holes)
        frames = GetFrameRange(stage, len(general_data))
        print(frames[-1])

        lhand_data = ImportHands(subj, trial, holes, "left")
        rhand_data = ImportHands(subj, trial, holes, "right")


        for f, frame in zip(range(len(frames)),frames):

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

        labels = [trial, holes, when_was_shown, stage]

    return rhand_dataframe, lhand_dataframe, labels




### Surface Touch Number based on Moving Positions ###
def TouchNumber(moving_positions):

    sphere_id = moving_positions['sphere_id']
    initial_positions = InitialSpherePositions()[0]

    initial_positions_density = pd.DataFrame()

    for id in sphere_id:

        if id not in initial_positions_density.values:

            new_row = pd.DataFrame([{"sphere_id": id, "x_position": initial_positions[id][0],
                                     "y_position": initial_positions[id][1], "z_position": initial_positions[id][2]}])

            for i in range(list(sphere_id).count(id)):
                initial_positions_density = pd.concat([initial_positions_density, new_row], ignore_index=True)

    return initial_positions_density




### Density of hand touches per hand and for both hands ###
def TouchDensity(trial, holes, stage, subject=None, when_was_shown=None, hand=False, surface=False, touch_number=False, three_dim=False):
    # i need to change when hand occurs in plot inputs

    labels = [trial, holes, when_was_shown, stage]

    if hand != False:

        rtouch_data,ltouch_data,labels = HandPositions(subject=subject, trial=trial, holes=holes, when_was_shown=when_was_shown, stage=stage, touch=True, hand=hand)
        lx,ly,lz = [[],[],[]]; rx,ry,rz = [[],[],[]]
        left = np.zeros(4); right = np.zeros(4); both = np.zeros(4)

        print('R len', len(rtouch_data))
        print('L len', len(ltouch_data))

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

        return right, left, both, labels

    if surface:
        moving_positions = SurfaceMoving(subject=subject, trial=trial, holes=holes, when_was_shown=when_was_shown, stage=stage)[1]

        x,y,z = moving_positions['x_position'], moving_positions['y_position'], moving_positions['z_position']

        KDE, xKDE, zKDE, values = GaussianKDE(x, z)
        surface = np.array([KDE, xKDE, zKDE, values], dtype=object)

        return surface, labels

    if touch_number:
        moving_positions = SurfaceMoving(subject=subject, trial=trial, holes=holes, when_was_shown=when_was_shown, stage=stage)[1]

        touch_number = TouchNumber(moving_positions)
        x,y,z = touch_number['x_position'], touch_number['y_position'], touch_number['z_position']

        KDE, xKDE, zKDE, values = GaussianKDE(x, z)
        surface_over_initial = np.array([KDE, xKDE, zKDE, values], dtype=object)

        return surface_over_initial, labels



#####################################
############ FUILD DATA #############
#####################################

### Get fluid count per hole ###
def FluidCountPerHole(trial, holes, when_was_shown):

    subjects = GetSubjects(holes, when_was_shown)

    caught_array = np.zeros(len(subjects), dtype=object)
    emitted_array = np.zeros(len(subjects), dtype=object)

    for s in range(len(subjects)):
        subj = subjects[s]

        general_data = ImportGeneral(subj, trial, holes)
        subj_caught = np.zeros(len(general_data), dtype=object)
        subj_emitted = np.zeros(len(general_data), dtype=object)

        for frame in range(len(general_data)):
            count = np.zeros(holes, dtype=object)

            for hole, fluid in zip(range(holes), general_data[frame][-8]):
                count[hole] = float(fluid.text)

            subj_caught[frame]= count
            subj_emitted[frame] = float(general_data[frame][-9].text)

        caught_array[s] = subj_caught
        emitted_array[s] = subj_emitted


    return caught_array, emitted_array


### Fluid score for each subject across time ###
def Score(trial, holes, when_was_shown):

    caught_all, emitted_all = FluidCountPerHole(trial, holes, when_was_shown)

    frames = []
    score_all= []

    for subj in range(len(caught_all)):

        with_fluid_frames = 0
        score = []

        for caught, emitted in zip(caught_all[subj], emitted_all[subj]):

            if emitted > 0 :

                with_fluid_frames += 1

                if holes == 1:
                    score.append(caught/emitted)
                if holes == 2:
                    score.append(np.array([2*np.min(caught/emitted)], dtype=object))

        frames.append(with_fluid_frames)
        score_all.append(score)

    # fix trials that ended earlier
    for subj in range(len(frames)):

        difference = np.max(frames) - frames[subj]

        for frame in range(difference):
            score_all[subj].append(score_all[subj][-1])

    return score_all


#### Mean and Standard Dev for fluid over trials ###
def MeanFluidScore(holes, when_was_shown):

    trials = np.arange(0,7,1)
    mean_trials = np.zeros((7,300,1))


    for t in range(len(trials)):

        trial = trials[t]
        trial_score = Score(trial, holes, when_was_shown)
        mean_trials[trial] = np.mean(np.array(trial_score), axis=0)[:300]

    std_trials = np.std(mean_trials, axis=0)
    #mean_trials = np.mean(mean_trials, axis=0)

    return mean_trials, std_trials











