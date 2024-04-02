import math

import numpy as np
import tifffile as tf
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

global baseline
baseline = 0

def change_in_fluorescence(selected_area, image_data):
    (x1, y1), (x2, y2) = selected_area
    selected_pixels = image_data[y1:y2, x1:x2]  # Extract selected pixels
    avg = np.mean(selected_pixels)
    return avg

image = tf.imread('../caroline_video1.tif')

fig, ax = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [10, 3]})

frame_index = 0
current_image = ax[0].imshow(image[frame_index])
ax[0].set_title(f'Frame {frame_index}')

selected_areas = []
frame_indices = []
change_in_fluorescence_data = []

def onselect(eclick, erelease):
    x1, y1 = int(min(eclick.xdata, erelease.xdata)), int(min(eclick.ydata, erelease.ydata))
    x2, y2 = int(max(eclick.xdata, erelease.xdata)), int(max(eclick.ydata, erelease.ydata))
    selected_area = ((x1, y1), (x2, y2))
    selected_areas.append(selected_area)
    print(f'Selected area: {selected_area}')
    draw_areas()

def draw_areas():
    global baseline
    ax[0].clear()
    ax[0].imshow(image[frame_index])
    ax[0].set_title(f'Frame {frame_index}')

    for area in selected_areas:
        (x1, y1), (x2, y2) = area
        width = x2 - x1
        height = y2 - y1
        rect = Rectangle((x1, y1), width, height, linewidth=1, edgecolor='r', facecolor='none')
        ax[0].add_patch(rect)

    ax[1].clear()
    ax[1].plot(frame_indices, change_in_fluorescence_data, color='blue')  # Plot all fluorescence data
    ax[1].set_xlabel('Frame Index')
    ax[1].set_ylabel('log(dF/F)')

def update(frame):
    global baseline
    global frame_index
    frame_index = frame

    if frame_index == 25 and not selected_areas:
        ani.event_source.stop()
    else:
        if frame_index >= 25:  # Start showing the graph from frame 25
            change_in_fluorescence_data.append(change_in_fluorescence(selected_areas[-1], image[frame_index]))
            if baseline == 0:
                baseline = change_in_fluorescence_data[0]
            change_in_fluorescence_data[-1] = math.log10(change_in_fluorescence_data[-1]/baseline)
            frame_indices.append(frame_index)
            ax[0].clear()
            ax[0].imshow(image[frame])
            ax[0].set_title(f'Frame {frame}')
            draw_areas()

selector = RectangleSelector(ax[0], onselect, useblit=True, button=[1], minspanx=5, minspany=5, spancoords='pixels', interactive=True)
ani = FuncAnimation(fig, update, frames=len(image))

plt.show()

# This saves it as a picture unfortunately
ani.save('change_in_fluorescence.gif', writer='pillow', fps=10)
