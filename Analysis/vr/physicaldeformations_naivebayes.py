from sklearn.model_selection import train_test_split
from imblearn.under_sampling import RandomUnderSampler
from time import time
from sklearn.naive_bayes import MultinomialNB, GaussianNB, ComplementNB
from sklearn import metrics
import matplotlib.pyplot as plt
import seaborn as sns

from jan_24.dataset_2 import *

#%%

#last_update: 19 Feb 24

data_manager = ManageData(Windows=True)
features = data_manager.load_features('hands')

""" 
    1. Applying Naive Bayes
    2. Calculating accuracy and generating classification report from test data
"""

def NB_(features, level, hand,  test_size=0.2, plot=True, up_vs_down=False):

  print(f'Level: {level} \nHand: {hand}')

  t = time()

  #naive_bayes_classifier = GaussianNB()
  #naive_bayes_classifier = MultinomialNB()
  naive_bayes_classifier = ComplementNB()

  if level == 1:
    X = features.loc[:,['CFDown', 'CFUp'],:, :, level,:,hand]
    y = X.index.get_level_values('syllable')
  if level == 2:
    X = features.loc[:,['LFDown', 'LFUp', 'RFDown', 'RFUp'],:,:,level,:,hand]
    y = X.index.get_level_values('syllable')
  if level == 'all':
    X = features.loc[:,['CFDown', 'CFUp', 'LFDown', 'LFUp', 'RFDown', 'RFUp'],:,:,:,:,hand]
    y = X.index.get_level_values('syllable')


  if up_vs_down:
    y = np.where(y.str.endswith('Up'), 'Up', 'Down')

  X_train, X_test, y_train, y_test = train_test_split(X.values, y, test_size=test_size)

  # Initialize random under-sampler to balance the classes in training data
  runs = RandomUnderSampler(random_state=42)
  X_train, y_train = runs.fit_resample(X_train, y_train)


  # ---------------------------------------------------------------

  labels, counts = np.unique(y_train, return_counts=True)
  nr_train_samples = dict(zip(labels, counts))
  labels, counts = np.unique(y_test, return_counts=True)
  nr_test_samples = dict(zip(labels, counts))
  print(f'train samples: {len(X_train)} {nr_train_samples}\ntest samples: {len(X_test)} {nr_test_samples}')

  naive_bayes_classifier.fit(X_train, y_train)

  training_time = time() - t
  print("train time: %0.3fs" % training_time)

  # predict the new document from the testing dataset
  t = time()
  pred_labels = naive_bayes_classifier.predict(X_test)

  val_time = time() - t
  print("test time:  %0.3fs" % val_time)

  # compute the performance measures
  score1 = metrics.accuracy_score(y_test, pred_labels)
  print("accuracy:   %0.3f" % score1)
  print(metrics.classification_report(y_test, pred_labels))
  print("confusion matrix:")
  cm = metrics.confusion_matrix(y_test, pred_labels)
  print(metrics.confusion_matrix(y_test, pred_labels))

  print('------------------------------')


  if plot:

    # Plot confusion matrix
    plt.figure(figsize=(6, 4.7))
    sns.heatmap(cm, annot=True, fmt='g', cmap='Blues', xticklabels=np.unique(y_test), yticklabels=np.unique(y_test))
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.show()



#%%
NB_(features.iloc[:, :-100], 1, 'Right')
NB_(features.iloc[:, :-100], 2, 'Right')
NB_(features.iloc[:, :-100], 'all', 'Right')
NB_(features.iloc[:, :-100], 1, 'Left')
NB_(features.iloc[:, :-100], 2, 'Left')
NB_(features.iloc[:, :-100], 'all', 'Left')
NB_(features.iloc[:, :-100], 'all', 'Right', up_vs_down=True)
NB_(features.iloc[:, :-100], 'all', 'Left', up_vs_down=True)

# up vs. down just the palm direction:
NB_(features.iloc[:, 200:300], 'all', 'Right', up_vs_down=True)
NB_(features.iloc[:, 200:300], 'all', 'Left', up_vs_down=True)
# random (just timestamps normalized):
NB_(features.iloc[:, -100:], 'all', 'Right', up_vs_down=True)
NB_(features.iloc[:, -100:], 'all', 'Left', up_vs_down=True)



