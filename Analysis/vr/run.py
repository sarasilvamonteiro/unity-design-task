from dataset import *
from jan24.draw_umap import draw_umap
#%%
ManageData()
#%%
# load csv
hands_syllables = ManageData().load_syllables('hands')
surface_syllables = ManageData().load_syllables('surface')
preprocess_hands = ManageData().preprocess(hands_syllables)
umap_values = ManageData().extract_values(preprocess_hands, as_array=False)

#%%
n = 5
d = 0.1
draw_umap(n_components=2,n_neighbors=n, min_dist=d, hand='Right', holes=1)
draw_umap(n_components=2,n_neighbors=n, min_dist=d, hand='Right', holes=2)
draw_umap(n_components=2,n_neighbors=n, min_dist=d, hand='Left', holes=1)
draw_umap(n_components=2,n_neighbors=n, min_dist=d, hand='Left', holes=2)


#%%













# naive bayes