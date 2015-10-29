import cv2
import Image
import ImageTk
from Tkinter import Tk, Label, Frame, Button


class App:

    def __init__(self, root):
        self.root = root
        self.img = self.readImage('/home/juan/Desktop/juan-gabriel-arias_juangarias@gmail.com.jpg')
        frame = Frame(root, width=100, height=100)

        # Put it in the display window
        self.label = Label(frame, image=self.img)
        self.label.pack()

        button = Button(frame, command=self.changeImage, text='OK')
        button.pack()

        frame.pack()

    def changeImage(self):
        self.img = self.readImage('/home/juan/Desktop/Bill_Clinton_0002.jpg')
        self.label.configure(image=self.img)
        self.label.pack()
        self.root.update_idletasks()

    def readImage(self, path):
        img = cv2.imread(path)

        # Rearrang the color channel
        b, g, r = cv2.split(img)
        img = cv2.merge((r, g, b))

        # Convert the Image object into a TkPhoto object
        im = Image.fromarray(img)
        return ImageTk.PhotoImage(image=im)


# Start the GUI
# A root window for displaying objects
root = Tk()
root.title('Sujeto encontrado')
root.geometry('600x600+100+100')

App(root)

root.mainloop()
