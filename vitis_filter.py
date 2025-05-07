import numpy as np

class WindowClass:
    def __init__(self):
        self.pix = np.zeros((5, 5))

    def __repr__(self):
        return f"\n{self.pix}\n"

def vitisFilter(inputStream, windowStream: list, bufPixStream=0):
    FILTER_SIZE: int = 5
    IMAGE_WIDTH: int = 10
    IMAGE_HEIGHT: int = 5

    LineBuffer = np.zeros((FILTER_SIZE-1, IMAGE_WIDTH+int((FILTER_SIZE-1)/2)))

    Window = WindowClass()

    num_pixels = IMAGE_WIDTH*IMAGE_HEIGHT

    read_ptr = 0

    # max_iterations = IMAGE_WIDTH*IMAGE_HEIGHT +IMAGE_WIDTH*((FILTER_SIZE-1)/2)+(FILTER_SIZE-1)/2

    for y in range(0,IMAGE_HEIGHT+int((FILTER_SIZE-1)/2)):
        for x in range(0, IMAGE_WIDTH+FILTER_SIZE-1):
            if read_ptr < num_pixels and x < IMAGE_WIDTH and y < IMAGE_HEIGHT:
                new_pixel = inputStream[read_ptr]
                read_ptr += 1
            else:
                new_pixel = 0

            for i in range(0, FILTER_SIZE):
                for j in range(0, FILTER_SIZE-1):
                    Window.pix[i,j] = Window.pix[i, j+1]

                if i < FILTER_SIZE-1 and x <= IMAGE_WIDTH:
                    Window.pix[i,FILTER_SIZE-1] = LineBuffer[i, x]
                else:
                    Window.pix[i,FILTER_SIZE-1] = new_pixel
        
            for i in range(0, FILTER_SIZE-2):
                if x < IMAGE_WIDTH: LineBuffer[i, x] = LineBuffer[i+1, x]
            if x < IMAGE_WIDTH:
                LineBuffer[FILTER_SIZE-2, x] = new_pixel

            if ((x > (FILTER_SIZE-1)/2-1 and x < IMAGE_WIDTH+(FILTER_SIZE-1)/2) and (y > (FILTER_SIZE-1)/2-1 and y < IMAGE_HEIGHT+(FILTER_SIZE-1)/2)):
                print(Window)
                windowStream.append(np.copy(Window))

    # for n in range(0,num_iterations):
    #     new_pixel = inputStream[n] if n < num_pixels else 0
    #     for i in range(0, FILTER_SIZE):
    #         for j in range(0, FILTER_SIZE-1):
    #             Window.pix[i,j] = Window.pix[i, j+1]
    #         Window.pix[i,FILTER_SIZE-1] = LineBuffer[i, col_ptr] if i < FILTER_SIZE-1 else new_pixel
    # 
    #     for i in range(0, FILTER_SIZE-2):
    #         LineBuffer[i, col_ptr] = LineBuffer[i+1, col_ptr]
    #     LineBuffer[FILTER_SIZE-2, col_ptr] = new_pixel
    # 
    #     if col_ptr == IMAGE_WIDTH-1:
    #         col_ptr = 0
    #     else:
    #         col_ptr = col_ptr + 1
    # 
    #     if (n >= ramp_up):
    #         print(Window)
    #         windowStream.append(np.copy(Window))


inputData = np.arange(10*5)
windowStream = []

vitisFilter(inputData, windowStream)
print(len(windowStream))
#for i in range(0, len(windowStream)):
#    print(windowStream[i])


        