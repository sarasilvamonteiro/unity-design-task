from auxiliary import *
import numpy as np
from scipy.spatial import Delaunay
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.ticker import NullFormatter
import matplotlib.tri as Tri
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.express as px
import seaborn as sns


#####################################
############### PLOTS ###############
#####################################

def Plot3DTopDown(density_data = None, position_data = None):

    # plot surface
    vertx = [-0.2, -0.2, 0.2, 0.2, -0.2]
    verty = [0.35, 0.75, 0.75, 0.35, 0.35]
    vertz = [0, 0, 0, 0, 0]
    vertices = [list(zip(vertx, verty, vertz))]
    poly = Poly3DCollection(vertices, alpha=1, facecolors=(227/255,186/292,207/255,1), edgecolors='none')


    if position_data != None:

        fig, ax = plt.subplots(figsize=(10, 6.5), subplot_kw={"projection": "3d"})
        ax.add_collection3d(poly)

        labels = position_data[-1]

        for hand_id,hand in enumerate(position_data[:-1]):

            hand_id, hand_cmap = HandDictionary(hand_id)

            if not hand.empty:
                print(hand_id)
                ax.plot(-hand['z_position'], hand['x_position'], zdir='z', zorder=10, color=plt.cm.get_cmap(hand_cmap)(0.1))


    if density_data != None:

        fig, ax = plt.subplots(figsize=(10, 6.5), subplot_kw={"projection": "3d"})
        ax.add_collection3d(poly)

        cmap = 'magma'

        #if its surface, density data will only have one value, if its hands, itll have 3 values and depending on the hand some will be empty
        for hand_or_surface in range(len(density_data)-1):

            KDE, xKDE, zKDE, values = density_data[hand_or_surface]

            if KDE != 0.0:

                if len(density_data) > 2 and hand_or_surface < 2:
                    hand_id, cmap = HandDictionary(hand_or_surface)

                xx, zz, g = ReshapeDensity(KDE)
                ax.contourf(-zz, xx, g, levels=np.linspace(4.7, np.max(g), 10), zdir='z', cmap=cmap, alpha=0.9)


        labels = density_data[-1]
        print(labels)


    hole_position = [0.15 + 0.01 * np.cos(np.linspace(0, 2*np.pi, 60)), 0 , 0.01 * np.sin(np.linspace(0, 2*np.pi, 60))]

    if labels[1] == 2:
        ax.plot(-0.3 + hole_position[2], hole_position[0], "o", color="black", label="hole")
        ax.plot(0.3 + hole_position[2], hole_position[0], "o", color="black")
    else:
        ax.plot(hole_position[2], hole_position[0], "o", color="black", label="hole")

    ax.view_init(azim=-90, elev=90)
    ax.set_xlabel('z')
    ax.set_ylabel('x')
    ax.set_zlabel('y')
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(-0.1, 0.9)
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(NullFormatter())
    ax.zaxis.set_major_formatter(NullFormatter())
    #plt.rcParams['grid.color'] = "gainsboro"
    plt.title('shown ' + str(labels[2]) + ' - trial ' + str(labels[0] + 1) + " - " + str(labels[3]))





def PlotTrajectory(position_data):

    plt.figure(figsize=(4,4))
    plt.plot([-0.2,-0.2,0.2,0.2,-0.2],[0.35,0.75,0.75,0.35,0.35])

    for hand_id,hand in enumerate(position_data[:-1]):

        hand_id, hand_cmap = HandDictionary(hand_id)

        if not hand.empty:
            print(hand_id)
            plt.plot(-hand['z_position'], hand['x_position'],color=plt.cm.get_cmap(hand_cmap)(0.1))


    plt.xlim((-0.5,0.5))
    plt.ylim((-0.1,0.9))


### Plot 3D side view with mesh and density contour at timeframe ###
def Plot3DDensity(mesh_data, density_data, calc_simplices=False):

    fig, ax = plt.subplots(figsize=(10, 6.5), subplot_kw={"projection": "3d"})

    if mesh_data[0].shape[0] > 3:
        x = mesh_data[0]; y = mesh_data[1]; z = mesh_data[2]
    if mesh_data[0].shape[0] == 3:
        x = mesh_data[:,0]; y = mesh_data[:,1]; z = mesh_data[:,2]

    if calc_simplices == True:
        points = np.stack((x, y), axis=1)
        tri = Delaunay(points)
        simplices = tri.simplices
    else:
        simplices = mesh_data[3]


    cmap = 'magma'

    y_scaler = 1.5

    #if its surface, density data will only have one value, if its hands, itll have 3 values and depending on the hand some will be empty
    for hand_or_surface in range(len(density_data)-1):

        KDE, xKDE, zKDE, values = density_data[hand_or_surface]

        if np.max((np.max(xKDE), np.max(zKDE))) > 1:
            print(np.max((xKDE, zKDE)))
            y_scaler = np.max((xKDE, zKDE))

        if KDE != 0.0:

            if len(density_data) > 2 and hand_or_surface < 2:
                hand_id, cmap = HandDictionary(hand_or_surface)

            xx, zz, g = ReshapeDensity(KDE)
            ax.contourf(-zz, xx, g, zdir ='z', offset = np.min(g), levels=np.linspace(4.7, np.max(g), 10), cmap=cmap, alpha=0.9)
            sns.kdeplot([value for idx,value in enumerate(values[0]) if value > 0 and value < 0.8], zs=-0.4, zdir='x', color=plt.cm.get_cmap(cmap)(0.1),label='x axis', zorder=-1)
            sns.kdeplot([-value for idx,value in enumerate(values[1]) if np.abs(value) < 0.4], zs=0.8, zdir='y', color=plt.cm.get_cmap(cmap)(0.1), label='z axis', zorder=-1)

    # i made the surface 1.5 times bigger for plotting and i scaled its height by the max density value
    #triang = Tri.Triangulation(x*1.5-0.1, y*1.5, np.array(simplices)) #x*1.5-0.1 (?)

    # mesh adjustments
    print(y_scaler)
    x = x * 1.1         # old: x*1.5-0.1 (?)
    y = y * 1.1-0.2     # old: y*1.5
    z = 2.5*y_scaler*z-2.5*0.59#y_scaler*y_scaler*z-(y_scaler*y_scaler*(y_scaler*0.07)) # old: y_scaler*z-0.2

    print(np.max(z))

    triang = Tri.Triangulation(x, y, np.array(simplices))
    ax.plot_trisurf(triang, z, linewidth=0.1, antialiased=True, color=(252/255,206/292,229/255,1), zorder=1000)



    labels = density_data[-1]
    print(labels)

    hole_position = [0.15 + 0.01 * np.cos(np.linspace(0, 2 * np.pi, 60)), 0,
                     0.01 * np.sin(np.linspace(0, 2 * np.pi, 60))]

    if labels[1] == 2:
        ax.plot(-0.3 + hole_position[2], hole_position[0], "o", color="black", label="hole")
        ax.plot(0.3 + hole_position[2], hole_position[0], "o", color="black")
    else:
        ax.plot(hole_position[2], hole_position[0], "o", color="black", label="hole")

    #ax.view_init(azim=-90, elev=90)
    ax.set_xlabel('z')
    ax.set_ylabel('x')
    ax.set_zlabel('y')
    ax.set_xlim(-0.4, 0.4) # -0.5, 0.5
    ax.set_ylim(0, 0.8) # -0.1, 0.9
    ax.set_zlim(0,y_scaler-0.6)
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(NullFormatter())
    ax.zaxis.set_major_formatter(NullFormatter())
    plt.rcParams['grid.color'] = "gainsboro"
    plt.title('shown ' + str(labels[2]) + ' - trial ' + str(labels[0]+1) + " - " + str(labels[3]))

    plt.show()





### Plot 3D mesh at timeframe ###
def Plot3DMesh(mesh_data, calc_simplices = False, color_func = False):

    if mesh_data[0].shape[0] > 3:
        x = mesh_data[0]
        y = mesh_data[1]
        z = mesh_data[2]
    if mesh_data[0].shape[0] == 3:
        x = mesh_data[:,0]
        y = mesh_data[:,1]
        z = mesh_data[:,2]

    if calc_simplices == True:
        points = np.stack((x, y), axis=1)
        tri = Delaunay(points)
        simplices = tri.simplices
    else:
        simplices = mesh_data[3]

    if color_func == True:
        color_func = mesh_data[4]
    else:
        color_func = np.random.rand(len(simplices))


    fig = ff.create_trisurf(x=x, y=y, z=z,
                            simplices=simplices, color_func = color_func, colormap=px.colors.sequential.ice_r[0], edges_color='rgb(0,0,0)',
                            #'rgb(135,206,235)' #Blackbody_r #(135/255,206/255,235/255,1)
                            aspectratio=dict(x=1, y=1, z=0.5),
                            width=600, height=600, title='Side Mesh', show_colorbar=False)
    fig.update_layout(scene = {'camera_eye': {"x": 1.5, "y": -1.5, "z": 0.5}})

    fig.show()



### Plot Fluid Score for all trials, if mean=True, plot mean and standard deviation, else plot one line per trial ###
def PlotFluidScore(holes, when_was_shown, mean=False):

    from functions_fluid import Score

    trials = np.arange(0,7,1)
    mean_trials = np.zeros((7,60,1))
    colors = plt.cm.Oranges(np.linspace(0.1, 1, 7)) #Oranges #copper_r
    plt.figure(figsize=(8, 5.5))
    plt.title(str(holes)+' well - shown '+str(when_was_shown), fontsize=18)
    plt.grid()

    for t in range(len(trials)):

        trial = trials[t]
        trial_score = Score(trial, holes, when_was_shown)
        mean_trials[trial] = np.mean(np.array(trial_score), axis=0)[np.arange(0,300,5)]

        if not mean:
            plt.plot(100*np.mean(np.array(trial_score), axis=0)[np.arange(0,300,5)], color=colors[t])

    std_trials = 100*np.std(mean_trials, axis=0)
    mean_trials = 100*np.mean(mean_trials, axis=0)

    if mean:
        plt.plot(mean_trials, c='darkmagenta')
        plt.fill_between(np.arange(0,len(mean_trials)),mean_trials[:,0], (mean_trials+std_trials)[:,0], alpha=0.3, edgecolor='darkmagenta', facecolor='C4')
        plt.fill_between(np.arange(0,len(mean_trials)),mean_trials[:,0], (mean_trials-std_trials)[:,0], alpha=0.3, edgecolor='darkmagenta', facecolor='C4')


    plt.ylim((0,100))
    #plt.xticks([])
    plt.yticks(fontsize=14)
    plt.xlabel('time', fontsize=16)
    plt.ylabel('% fluid collected', fontsize=16)
    plt.grid()
    plt.show()


