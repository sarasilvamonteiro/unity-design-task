#%%
import matplotlib.pyplot as plt
import numpy as np

# Define colors for each corner
colors = [
    [1, 0, 0],  # Red (top-left corner)
    [0, 1, 0],  # Green (top-right corner)
    [0, 0, 1],  # Blue (bottom-left corner)
    [1, 1, 0] ,  # Yellow (bottom-right corner)
]
colors = [
    [0, 1, 0],  # Green (top-left corner)
    [1, 0, 0],  # Red (top-right corner)
    [1, 1, 0],  # Yellow (bottom-left corner)
    [0, 0, 1] ,  # Blue (bottom-right corner)
]


# Create a 2D grid with color values corresponding to corners
grid_size = 100
color_map = np.zeros((grid_size, grid_size, 3))

for i in range(grid_size):
    for j in range(grid_size):
        color_map[i, j] = (
            (colors[0][0] * (grid_size - i) * (grid_size - j) / (grid_size ** 2)) +  # Red component
            (colors[1][0] * i * (grid_size - j) / (grid_size ** 2)) +               # Green component
            (colors[2][0] * (grid_size - i) * j / (grid_size ** 2)) +               # Blue component
            (colors[3][0] * i * j / (grid_size ** 2)),                             # Yellow component
            (colors[0][1] * (grid_size - i) * (grid_size - j) / (grid_size ** 2)) +
            (colors[1][1] * i * (grid_size - j) / (grid_size ** 2)) +
            (colors[2][1] * (grid_size - i) * j / (grid_size ** 2)) +
            (colors[3][1] * i * j / (grid_size ** 2)),
            (colors[0][2] * (grid_size - i) * (grid_size - j) / (grid_size ** 2)) +
            (colors[1][2] * i * (grid_size - j) / (grid_size ** 2)) +
            (colors[2][2] * (grid_size - i) * j / (grid_size ** 2)) +
            (colors[3][2] * i * j / (grid_size ** 2))
        )

# Display the colormap
plt.imshow(color_map)
plt.axis('off')  # Turn off the axis
plt.title('2D Colormap with Different Corners')
plt.show()

np.save('surface_colormap.npy', color_map)