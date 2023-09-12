import numpy as np
from scipy.stats import gaussian_kde
from sklearn import preprocessing
import pandas as pd

### Sphere position and ID (correct id for aug23) ###
def SphereID(sphere_data, sphere, timeframe):

    sphere_position = sphere_data[timeframe][sphere]
    sphere_id = int(sphere_position.tag[-4:])
    correct_id = int(2000 + (sphere_id - 2000) /2) # fix sphere id (apply to aug23 data, it has duplicated sphere data)

    return sphere_position, sphere_id, correct_id

### Hand index and colormap dictionary ###
def HandDictionary(hand):

    hand_dict = {'right': 0, 'left': 1, 'both': 2}
    color_dict = {'left': 'pink', 'right': 'Reds_r', 'both': 'viridis'}

    if type(hand) == type(0):
        hand_dict = {0: 'right',  1: 'left', 2: 'both'}

        return hand_dict[hand], color_dict[hand_dict[hand]]

    else:

        return hand_dict[hand], color_dict[hand]

### Get framerange per stage ###
def GetFrameRange(stage, len_data):

    if stage == 'early':
        frames = np.arange(0, int(len_data/3),1)
    if stage == 'middle':
        frames = np.arange(int(len_data/3),2*int(len_data/3),1)
    if stage == 'late':
        frames = np.arange(2*int(len_data/3), len_data,1)
    if stage == 'all':
        frames = range(len_data)

    return frames

### Get subject number ###
# Subject number might change depending on the task design
def GetSubjects(holes, when_was_shown):

    all_subjects = np.array([[5,8,14,15,17],[9,11,12,13,16]])

    if when_was_shown == 'first':
        subjects = all_subjects[holes-1]
        print(subjects)

    elif when_was_shown == 'last':
        subjects = all_subjects[2-holes]
        print(subjects)

    elif when_was_shown == 'all':
        subjects = np.hstack(all_subjects)

    return subjects

### Normalize data ###
def Normalize(x,y=np.random.rand(3),z=np.random.rand(3)):

    normx = (x-np.min(x))/(np.max(x) - np.min(x))
    normy = (y-np.min(y))/(np.max(y) - np.min(y))
    normz = (z-np.min(z))/(np.max(z) - np.min(z))

    return normx, normy, normz

def NormalizeHands(lhand_data, rhand_data):

    x, y, z = np.append(lhand_data[:, 0], rhand_data[:, 0]), \
        np.append(lhand_data[:, 1], rhand_data[:, 1]), \
        np.append(lhand_data[:, 2], rhand_data[:, 2])
    x_norm = (x - np.min(x)) / (np.max(x) - np.min(x))
    y_norm = (y - np.min(y)) / (np.max(y) - np.min(y))
    z_norm = (z - np.min(z)) / (np.max(z) - np.min(z))

    return x_norm, y_norm, z_norm

### Scale data between 0 and 1, transforming max x value=1 ###
def MaxAbsScaler(x):

    max_abs_scaler = preprocessing.MaxAbsScaler()
    x_scaled = max_abs_scaler.fit_transform(x)
    df = pd.DataFrame(x_scaled)

    return df

def MinMaxScaler(x):

    max_abs_scaler = preprocessing.MinMaxScaler()
    x_scaled = max_abs_scaler.fit_transform(x)
    df = pd.DataFrame(x_scaled)

    return df


def GaussianKDE(x,y=None):

    idxx = np.array(x).argsort()
    xKDE = gaussian_kde(x)(x)
    xKDE = xKDE[idxx]

    print(type(y))
    if type(y) != type(None):

        idxy = np.array(y).argsort()
        yKDE = gaussian_kde(y)(y)
        yKDE = yKDE[idxy]

        values = np.vstack([x, y])
        KDE = gaussian_kde(values)

        return KDE,xKDE,yKDE,values
    else:
        return xKDE


### Reshape data for plot ###
def ReshapeDensity(kernel):
    xmin, xmax = -1, 1
    ymin, ymax = -1, 1

    # Peform the kernel density estimate
    xx, yy = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
    positions = np.vstack([xx.ravel(), yy.ravel()])

    g = np.reshape(kernel(positions).T, xx.shape)

    return xx,yy,g