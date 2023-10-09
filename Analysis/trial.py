from auxiliary import *
import xml.etree.ElementTree as ET


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

        SubjectWarning(self, subj)

        if subj in self.subjects:

            #info = np.load(get info file and check how many trials)
            #self.nr_trials = ....

            self.method_step = 1
            print(self.method_step, ' ImportGeneral() subject: ', int(subj))

            #'C:/Users/teaching lab/Desktop/
            tree = ET.parse(r"C:\Users\Sara\Desktop\DesignMotorTask\Data\subject_" + str(int(subj))
                            + "\\" + str(self.holes) + "_holes_1_flows_general_" + str(self.trial))

                #(r'/Users/smonteiro/Desktop/DesignMotorTask/Data/subject_' + str(int(subj))
                            #+ "/" + str(self.holes) + "_holes_1_flows_general_" + str(self.trial) + ".xml")
            root = tree.getroot()

            return (root)