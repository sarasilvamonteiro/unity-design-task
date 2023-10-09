from trial import *
from features import *
from surface import *

class Hands(Trial, FeatureExtraction):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.objects = 2


    def ImportHands(self, hand, subj=None):

        SubjectWarning(self, subj)

        if subj in self.subjects:

            self.method_step = 1
            print(self.method_step, " ImportHands('" + str(hand)+ "') subject: ", int(subj))

            tree = ET.parse(r"C:\Users\Sara\Desktop\DesignMotorTask\Data\subject_" + str(int(subj))
                            + "\\" + str(self.holes) + "_holes_1_flows_" + str(hand) + "_hand_data_" + str(self.trial))
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



