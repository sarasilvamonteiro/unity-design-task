import xml.etree.ElementTree as ET

#####################################
############ IMPORT DATA ############
#####################################
def ImportGeneral(subject, trial, holes):
    #'C:/Users/teaching lab/Desktop/
    tree = ET.parse(r"C:\Users\Sara\Desktop\Unity\Clayxels\Data\subject_" + str(subject) + "\\" + str(holes) + "_holes_1_flows_general_" + str(trial))
    root = tree.getroot()

    return (root)

def ImportInitialPositions():

    tree = ET.parse(r'C:\Users\Sara\Desktop\Unity\Clayxels\Data\initial_positions')
    root = tree.getroot()

    return (root)

def ImportIdealPositions(holes):

    tree = ET.parse(r"C:\Users\Sara\Desktop\Unity\Clayxels\Data" + str(holes) + "_holes_ideal_positions_0")
    root = tree.getroot()

    return (root)

def ImportSpheres(subject, trial, holes):

    tree = ET.parse(r"C:\Users\Sara\Desktop\Unity\Clayxels\Data\subject_" + str(subject) + "\\" + str(holes) + "_holes_1_flows_sphere_position_" + str(trial))
    root = tree.getroot()

    return (root)

def ImportHands(subject, trial, holes, hand):

    tree = ET.parse(r"C:\Users\Sara\Desktop\Unity\Clayxels\Data\subject_" + str(subject) + "\\" + str(holes) + "_holes_1_flows_" + str(hand) + "_hand_data_" + str(trial))
    root = tree.getroot()

    return (root)


