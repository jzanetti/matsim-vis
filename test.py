# importing required libraries
import matplotlib.animation as animation
import numpy as np
from matplotlib import pyplot as plt

# initializing a figure
fig = plt.figure()
  
# labeling the x-axis and y-axis
axis = plt.axes(xlim=(0, 1000),  ylim=(0, 1000))
  
# lists storing x and y values
x, y = [], []
  
line, = axis.plot(0, 0)
  
  
def animate(frame_number):
    x.append(frame_number)
    y.append(frame_number)
    line.set_xdata(x)
    line.set_ydata(y)
    return line,
  
  
anim = animation.FuncAnimation(fig, animate, frames=1000, 
                               interval=20, blit=True)
fig.suptitle('Straight Line plot', fontsize=14)
  
# saving to m4 using ffmpeg writer
writervideo = animation.FFMpegWriter(fps=60)
anim.save('increasingStraightLine.mp4', writer=writervideo)
plt.close()
