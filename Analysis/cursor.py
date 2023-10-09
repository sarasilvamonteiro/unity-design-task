from import_data import *
from auxiliary import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#####################################
############ SPHERE DATA ############
#####################################


### Surface positions that were touched by cursor ###
def TouchedSpherePositions(trial, holes, when_was_shown, stage='all'):

    subjects = GetSubjects(holes,when_was_shown)
    sphere_data = pd.DataFrame()

    for subj in subjects:
        data = ImportGeneral(subj, trial, holes)

        #sphere_position = np.zeros((len(data),3))
        last_frame = 0

        frames = GetFrameRange(stage, len(data))

        for frame in frames:
            timestamp = float(data[frame][-2].text)
            sphere_id = int(data[frame][2].text)
            fluid_left = float(data[frame][9].text)

            # to get position up until the fluid stops
            if sphere_id != 0 and fluid_left != 0:

                frame_position = np.zeros(3)

                for axis, position in zip(range(3), data[frame][3]):
                    frame_position[axis] = float(position.text)

                #sphere_position[frame] = frame_position
                last_frame += 1

                new_row = pd.DataFrame([{"sphere_id": sphere_id, "x_position": frame_position[0],
                                         "y_position": frame_position[1], "z_position": frame_position[2],
                                         "timestamp": timestamp}])

                sphere_data = pd.concat([sphere_data, new_row], ignore_index=True)

    return sphere_data


### Number of clicks on surface per stage ###
def NumberOfClicks(trial, holes, when_was_shown, stage='all'):

    surface_data = TouchedSpherePositions(trial, holes, when_was_shown, stage)
    spheres = []
    sphere_counter = []
    dict_counter = {}

    for idx, sphere in zip(np.arange(0,len(surface_data),1), surface_data['sphere_id']):

        if idx == 0:
            spheres.append(sphere)

        if idx != 0 and sphere != surface_data['sphere_id'][idx-1]:
            spheres.append(sphere)

    for sphere in spheres:
        sphere_counter.append(np.array([sphere, spheres.count(sphere)]))
        dict_counter[sphere] = spheres.count(sphere)

    return dict_counter#np.array(sphere_counter)


### Duration of clicks on surface per stage ###
def DurationOfClicks(trial, holes, when_was_shown, stage='all'):

    surface_data = TouchedSpherePositions(trial, holes, when_was_shown, stage)
    spheres = []
    click_counter = []
    dict_counter = {}

    for sphere in surface_data['sphere_id']:

        spheres.append(sphere)

    for sphere in spheres:
        click_counter.append(np.array([sphere, spheres.count(sphere)]))
        dict_counter[sphere] = spheres.count(sphere)

    return dict_counter #p.array(click_counter)




### Plot agent position in environment ###
def PlotAgent(trial, holes, when_was_shown, plot_axis):

    surface_position = [5.6, 4.5, 0]
    surface_edges =[[3.35, 3.35, 7.85, 7.85, 3.35] ,[4.5, 4.5, 4.5, 4.5, 4.5] , [-2.25, 2.25, 2.25, -2.25, -2.25]]
    flow_position = [10, 6.5 , 0]
    hole_position = [1.5 + 0.2 * np.cos(np.linspace(0, 2*np.pi, 60)), 0 , 0.2 * np.sin(np.linspace(0, 2*np.pi, 60))]

    subjects = GetSubjects(holes,when_was_shown)

    plt.figure(figsize=(4,4))
    plt.title("Agent position - top down view")

    plt.xticks([])
    plt.yticks([])
    plt.grid(True)
    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    loc = 3

    if plot_axis[1] == 1:
        plt.ylim(0, 20)
        hole_position = [0,0,0]
        loc = 2

    # plot flow
    plt.plot(flow_position[plot_axis[0]],  flow_position[plot_axis[1]], "s", color="dimgrey", label="flow")
    # plot surface
    plt.plot(surface_edges[plot_axis[0]], surface_edges[plot_axis[1]], color="skyblue", label='surface')
    plt.fill_between(surface_edges[plot_axis[0]][0:2], surface_edges[plot_axis[1]][0:2],  surface_edges[plot_axis[1]][2:4], color="skyblue")
    # plot hole
    if holes == 2 and not plot_axis[1] == 1:
        plt.plot(-3 + hole_position[plot_axis[0]], hole_position[plot_axis[1]], "o", color="dimgrey", label="hole")
        plt.plot(3 + hole_position[plot_axis[0]], hole_position[plot_axis[1]], "o", color="dimgrey")
    else:
        plt.plot(hole_position[plot_axis[0]], hole_position[plot_axis[1]], "o", color="dimgrey", label="hole")


    for subj in subjects:

        if subj == 0 or subj == 5:
            label_0 = 'initial_position'
            label_1 = 'end_position'

        else:
            label_0 = ''
            label_1 = ''

        data = ImportGeneral(subj,trial,holes)

        agent_position = np.zeros((len(data),3))
        last_frame = 0

        for frame in range(len(data)):

            fluid_left = float(data[frame][9].text)

            # to get position up until the fluid stops
            if fluid_left != 0:

                frame_position = np.zeros(3)

                for axis, position  in zip(range(3), data[frame][0]):
                    frame_position[axis] = float(position.text)

                agent_position[frame] = frame_position
                last_frame += 1

        plt.legend(loc=loc)
        plt.plot(agent_position[:last_frame, plot_axis[0]], agent_position[:last_frame, plot_axis[1]], "-")
        plt.plot(agent_position[0, plot_axis[0]], agent_position[0, plot_axis[1]], "o", color="black", fillstyle='none', label=label_0)
        plt.plot(frame_position[plot_axis[0]], frame_position[plot_axis[1]], "x", color = "black", label=label_1)

