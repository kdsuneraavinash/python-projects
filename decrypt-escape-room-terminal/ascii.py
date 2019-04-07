import sys, random, argparse 
import numpy as np 
import math 
import cv2
  
gscale1 = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
gscale2 = '@%#*+=-:. '
  
def get_average_l(image): 
    # Given PIL Image, return average value of grayscale value 
    w,h = image.shape[:2]
    if len(image.shape) == 3:
        d = image.shape[-1]
    else:
        d = 1
    return np.average(image.reshape(w*h*d)) 


def covert_image_to_ascii(file_name, cols, scale, more_levels): 
    image = cv2.imread(file_name, 0)
    return frame_to_ascii_art(image, cols, scale, more_levels)

def frame_to_ascii_art(image, cols, scale, more_levels): 
    """ 
    Given Image and dims (rows, cols) returns an m*n list of Images  
    """
    global gscale1, gscale2 
  
    W, H = image.shape[0], image.shape[1] 
    scale = W/H if scale == None else scale

    w = W/cols 
  
    h = w/scale 
    rows = int(H/h) 
    
    if cols > W or rows > H: 
        return
  
    aimg = []
    for j in range(rows): 
        y1 = int(j*h) 
        y2 = int((j+1)*h) 

        if j == rows-1: 
            y2 = H 
        aimg.append("") 
  
        for i in range(cols): 
            x1 = int(i*w) 
            x2 = int((i+1)*w)
            if i == cols-1: 
                x2 = W


            img = image[x1 : x2, y1 : y2]
            avg = int(get_average_l(img)) 
  
            if more_levels: 
                gsval = gscale1[int((avg*69)/255)] 
            else: 
                gsval = gscale2[int((avg*9)/255)] 
  
            aimg[j] += gsval 
    return aimg 

if __name__ == "__main__":
    img = covert_image_to_ascii('snapshot.jpeg', 100, None, False)
    img = '\n'.join(img)
    print(img)