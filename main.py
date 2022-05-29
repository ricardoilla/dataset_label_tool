import tkinter
from tkinter import *
import cv2
import PIL.Image, PIL.ImageTk
import json
import os
import time

next_path = 'imgs/forward.jpg'
previous_path = 'imgs/backward.jpg'
save_path = 'imgs/save.jpg'
input_path = 'videos/2.avi'
output_path = 'output/'


class App:
    def __init__(self, root, window_title, video_source=0):
        self.window = root
        self.window.title(window_title)
        self.video_source = video_source
        self.actual_frame = None
        self.actual_frame_number = 0
        self.actual_coords = [0, 0]
        self.detected = False

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(root, width = self.vid.width, height = self.vid.height)

        # Next Button
        next_photo = PIL.ImageTk.PhotoImage(PIL.Image.open(next_path))
        self.btn_next = tkinter.Button(self.window, width=50, image=next_photo, command=self.next)

        # Previous Button
        previous_photo = PIL.ImageTk.PhotoImage(PIL.Image.open(previous_path))
        self.btn_previous = tkinter.Button(self.window, width=50, image=previous_photo, command=self.previous)

        # Save Button
        save_photo = PIL.ImageTk.PhotoImage(PIL.Image.open(save_path))
        self.btn_save = tkinter.Button(self.window, width=50, image=save_photo, command=self.save)

        self.text_pane = Text(self.window, height=2, width=30)

        self.canvas.grid(row=0, column=0)
        self.text_pane.grid(row=1, column=0)
        self.btn_save.grid(row=2, column=0, sticky='n')
        self.btn_next.grid(row=2, column=0, sticky='e')  # right position
        self.btn_previous.grid(row=2, column=0, sticky='w')  # left position

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update('forward')

        self.canvas.bind('<Button-1>', self.draw_pointer)
        self.window.mainloop()

    def next(self):
        self.update('forward')

    def previous(self):
        self.update('backward')

    def update(self, direction):
        # Get a frame from the video source
        ret, self.actual_frame, self.actual_frame_number = self.vid.get_frame(direction)
        if str(self.actual_frame_number) in metadata.keys():
            # If the frame was previously saved
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.actual_frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
            x = metadata[str(self.actual_frame_number)]["x"]
            y = metadata[str(self.actual_frame_number)]["y"]
            self.detected = metadata[str(self.actual_frame_number)]["detected"]
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="red")
            self.text_pane.delete(1.0, tkinter.END)
            self.text_pane.insert(tkinter.END, "detected={}, x={}, y={}".format(self.detected, x, y))
        else:
            # If the frame is new
            self.detected = False
            self.actual_coords=[0, 0]
            self.text_pane.delete(1.0, tkinter.END)
            # print('Frame number=', self.actual_frame_number)
            if ret:
                self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.actual_frame))
                self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

    def draw_pointer(self, event):
        # When the user click
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.canvas.create_oval(event.x-5, event.y-5, event.x+5, event.y+5, fill="red")
        self.actual_coords = [event.x, event.y]
        self.detected = True
        self.text_pane.delete(1.0, tkinter.END)
        self.text_pane.insert(tkinter.END, "detected={}, x={}, y={}".format(self.detected, event.x, event.y))


    def save(self):
        cv2.imwrite(('{}{}.jpg').format(output_path, self.actual_frame_number), self.actual_frame)
        metadata[str(self.actual_frame_number)] = {"detected":str(self.detected), "x":self.actual_coords[0], "y":self.actual_coords[1]}
        with open(output_path+'metadata.json', 'w') as json_file:
            json.dump(metadata, json_file)
            self.text_pane.insert(tkinter.END,'\nSaved!')




class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(input_path)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)


    def get_frame(self, direction):
        frame_number = 0
        if self.vid.isOpened():
            next_frame = self.vid.get(cv2.CAP_PROP_POS_FRAMES)
            current_frame = next_frame - 1
            previous_frame = current_frame - 1

            if direction == 'forward':
                self.vid.set(cv2.CAP_PROP_POS_FRAMES, next_frame)
                frame_number = next_frame
                ret, frame = self.vid.read()
                if ret:
                    # Return a boolean success flag and the current frame converted to BGR
                    return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), int(frame_number))
                else:
                    return (ret, None)
            else:
                if previous_frame >= 0:
                    self.vid.set(cv2.CAP_PROP_POS_FRAMES, previous_frame)
                    frame_number = previous_frame

                else:
                    self.vid.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    frame_number = 0
                ret, frame = self.vid.read()
                if ret:
                    # Return a boolean success flag, the current frame converted to BGR and the frame number
                    return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), int(frame_number))
                else:
                    return (ret, None)
        else:
            return False, None

    # Release the video source when the object is destroyed
    def __del__(self):

        if self.vid.isOpened():
            self.vid.release()





open(output_path+'metadata.json','a+')

with open(output_path+'metadata.json', 'r') as jsonFile:
    try:
        metadata = json.load(jsonFile)
    except:
        metadata = {}

print('######################')
print('Previous Metadata:')
print(metadata)
print('######################')
# Create a window and pass it to the Application object
App(tkinter.Tk(), "Stylus Labeller Tool")