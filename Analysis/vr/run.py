from jan_24.draw_umap_2 import *
#%%
data_manager = ManageData(Windows=True)
features = data_manager.load_features('hands')

#%%
hands_syllables = data_manager.load_syllables('hands')
surface_syllables = data_manager.load_syllables('surface')
preprocess_hands = data_manager.load_preprocessed_syllables('hands')
#%%
n = 5
d = 0.1
draw_umap(features.iloc[:, :-100], n_components=2,n_neighbors=n, min_dist=d, hand='Right', holes=1, pca_components=10)
draw_umap(features.iloc[:, :-100], n_components=2,n_neighbors=n, min_dist=d, hand='Right', holes=2, pca_components=10)
draw_umap(features.iloc[:, :-100], n_components=2,n_neighbors=n, min_dist=d, hand='Left', holes=1, pca_components=10)
draw_umap(features.iloc[:, :-100], n_components=2,n_neighbors=n, min_dist=d, hand='Left', holes=2, pca_components=10)


#%%
n = 5
d = 0.1
draw_umap_by_trial(features, n_components=2,n_neighbors=n, min_dist=d, hand='Right', holes=1)









# naive bayes
