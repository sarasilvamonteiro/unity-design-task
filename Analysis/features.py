from trial import *

class FeatureExtraction():

    def __init__(self):
        self.section_list = ['LCornerDown_i', 'RCornerDown_i', 'LEdgeUp_i', 'REdgeUp_i',
                             'CenterFrontDown_i', 'CenterFrontUp_i', 'LFrontUp_i', 'LFrontDown_i',
                             'RFrontUp_i', 'RCornerUp_i', 'LCornerUp_i', 'BackUp_i']

    def ImportSurfaceState(self, subj=None):
        '''
        Imports SurfaceMoving() from Surface() class.
        This is to escape circular dependency.
        :return:
        '''

        from surface import Surface

        surface_state = Surface(self.trial, self.holes, self.when_was_shown,
                                    subj, self.stage, self.timeframe).SurfaceMoving()
        return surface_state

    def ImportFeatures(self, subj=None):

        subj_features = pd.DataFrame()

        for subj in self.subjects:

            try:
                subj_features = pd.concat((subj_features, pd.read_excel('subj' + str(subj) + '_feature_extraction.xlsx')))
            except:
                pass

        self.method_step = 1
        print(self.method_step, " ImportFeatures()")

        return subj_features


    def FeatureTimeframes(self, feature):
        """
        :param subj: subject
        :param feature:
        :return:
        """
        data = self.ImportFeatures()

        if feature[-2:] == '_i' or feature[-2:] == '_f':
            feature = feature[:-2]

        feature_i = data[feature + '_i']
        feature_f = data[feature + '_f']

        # whole movement; movement when moving surface; movement
        whole = []; moving = []; movig_start_to_end = []

        for object in range(self.objects):

            whole.append(pd.DataFrame())
            moving.append(pd.DataFrame())
            movig_start_to_end.append(pd.DataFrame())

        def SaveToDataFrame(first_row):

            new_row = pd.DataFrame([{first_row[0]: first_row[1],
                                     "x_position": frame_position[0],
                                     "y_position": frame_position[1],
                                     "z_position": frame_position[2],
                                     "timestamp": timestamp, "sequence": sequence, "feature": feature,
                                     "trial": trial, "holes": holes}])
            # whole movement
            whole[i] = pd.concat([whole[i], new_row], ignore_index=True)
            # movement only when surface is being deformed (is moving)
            if is_surface_moving[frame]:
                moving[i] = pd.concat([moving[i], new_row], ignore_index=True)
            # whole movement since surface starts being deformed until it stops
            # if movement is only one frame, and timestamp is the first timestamp of the interval
            if len(moving_time_interval) == 1 and timestamp == moving_time_interval[0]:
                movig_start_to_end[i] = pd.concat([movig_start_to_end[i], new_row],
                                                  ignore_index=True)
            # if movement has many frams and timestamp is inside the interval
            elif len(moving_time_interval) > 1 and timestamp >= moving_time_interval[
                0] and timestamp < moving_time_interval[-1]:
                movig_start_to_end[i] = pd.concat([movig_start_to_end[i], new_row],
                                                  ignore_index=True)


        last_data = []
        sequence = -1
        # iterate over rows in data
        for subj, trial, holes, interval in zip(data.subject, data.trial, data.holes, range(len(feature_i))):

            # if feature row values aren't nan
            if not np.isnan(feature_i[interval]):
                sequence += 1
                # import new data if trial is different
                if [subj, trial, holes] != last_data:

                    print(self.method_step, ' Trial: ', trial)

                    data_list = []
                    general_data = self.ImportGeneral(subj)

                    try:
                        data_list.append(self.ImportHands(subj=subj, hand='right'))  # 1 # 0
                        data_list.append(self.ImportHands(subj=subj, hand='left'))  # 2 # 1
                    except AttributeError:
                        data_list.append(self.ImportSpheres(subj))

                    surface_moving = self.ImportSurfaceState(subj)#(self.trial, self.holes, self.when_was_shown,
                                    #subj, self.stage, self.timeframe).SurfaceMoving()
                    is_surface_moving = surface_moving[0][0][0][0]
                    moving_timestamps = surface_moving[0][0][1]

                # run through all frames
                for frame in range(len(general_data)):

                    timestamp = float(general_data[frame][-3].text)

                    # get the time interval in which the surface is moving
                    moving_time_interval = [value for idx, value in enumerate(moving_timestamps) if
                                            value >= feature_i[interval] and value <= feature_f[interval]]

                    # get the frames that fit in the feature interval
                    if timestamp >= feature_i[interval] and timestamp < feature_f[interval]:

                        for i, element_data in enumerate(data_list):

                            try:

                                for sphere in np.arange(0, 2 * self.nr_spheres, 2):

                                    sphere_info = element_data[frame][sphere]
                                    sphere_id, correct_id = SphereID(sphere_info)
                                    frame_position = np.zeros(3)

                                    for axis, position in zip(range(3), sphere_info):
                                        frame_position[axis] = float(position.text)

                                    SaveToDataFrame(first_row=["sphere_id", correct_id])

                            except AttributeError:

                                # -2 for left, -1 for right
                                hand_id = -(i + 1)  # left i > right i

                                frame_position = np.zeros(3)
                                palm = element_data[frame][0]

                                for axis, position in zip(range(3), palm):
                                    frame_position[axis] = float(position.text)

                                # if general_data[frame][hand_id] == true it means hand is being tracked
                                # if data.hand[interval] == HandDictionary(hand_id) it means the hand ...
                                if general_data[frame][hand_id].text == 'true' and data.hand[interval] == \
                                        HandDictionary(-hand_id - 1)[0]:

                                    hand_title = general_data[frame][hand_id].tag[:-4]
                                    SaveToDataFrame(first_row=["hand", hand_title])


            last_data = [subj, trial, holes]

        self.method_step += 1
        print(self.method_step, " FeatureTimeframes() subject: ", int(subj))

        return whole, moving, movig_start_to_end


