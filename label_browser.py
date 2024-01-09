import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import pandas as pd
import csv
from datetime import datetime
class_f=[]
save_file_name=[]
class ImageLabelerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Image browser')
        self.img_name=None
        self.image_list = []
        self.current_image_index = 0
        self.is_playing = True
        self.image_labels = {}
        self.rotation_angle = 0  # 初始化旋转角度为0
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side='left')

        self.open_button = tk.Button(self.left_frame, text='Open folder', command=self.open_folder)
        self.open_button.pack()

        self.canvas = tk.Canvas(self.left_frame, width=600, height=600, bg='grey')
        self.canvas.pack()
        self.navigation_frame = tk.Frame(self.left_frame)
        self.navigation_frame.pack()
        self.prev_button = tk.Button(self.navigation_frame, text='Prev.', command=self.show_prev_image)
        self.prev_button.pack(side='left')

        self.pause_button = tk.Button(self.navigation_frame, text='Pause', command=self.toggle_pause)
        self.pause_button.pack(side='left', padx=10)

        self.next_button = tk.Button(self.navigation_frame, text='Next', command=self.show_next_image)
        self.next_button.pack(side='left')

        # Flip button
        self.flip_button = tk.Button(self.navigation_frame, text='Flip', command=self.flip_image)
        self.flip_button.pack(side='left')

        # Zoom in button
        self.zoom_in_button = tk.Button(self.navigation_frame, text='Zoom in', command=lambda: self.zoom_image(1.25))
        self.zoom_in_button.pack(side='left')

        # Zoom out button
        self.zoom_out_button = tk.Button(self.navigation_frame, text='Zoom out', command=lambda: self.zoom_image(0.8))
        self.zoom_out_button.pack(side='left')

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side='right', fill='y')

        # 文件名标签
        self.filename_label = tk.Label(self.right_frame, text="")
        self.filename_label.pack(side='top', anchor='ne')

        self.label_selection_label = tk.Label(self.right_frame, text="Label Selection")
        self.label_selection_label.pack()

        self.level_var = tk.StringVar()
        self.level_var.set("None")

        self.levels = ["Grade 0", "Grade 1", "Grade 2", "Grade 3", "Grade 4"]
        self.radio_buttons = []
        for level in self.levels:
            rb = tk.Radiobutton(self.right_frame, text=level, variable=self.level_var, value=level)
            rb.pack(anchor='w')
            self.radio_buttons.append(rb)
            
            
    def flip_image(self):
        # Open the current image using PIL
        pil_image = Image.open(self.image_list[self.current_image_index])
        # Update the rotation angle
        self.rotation_angle = (self.rotation_angle - 90) % 360  # 逆时针旋转90度
        # Rotate the image by the updated angle
        rotated_image = pil_image.rotate(self.rotation_angle, expand=True)  # expand=True to resize the image dimensions if necessary
        # Convert the rotated image to a PhotoImage object and update the display
        self.photo_image = ImageTk.PhotoImage(rotated_image)
        self.canvas.itemconfig(self.canvas_image, image=self.photo_image)



    def zoom_image(self, zoom_factor):
        # Open the original image using PIL
        pil_image = Image.open(self.image_list[self.current_image_index])
        # Get the size of the original image
        width, height = pil_image.size
        # Calculate the new size based on the zoom factor
        new_size = (int(width * zoom_factor), int(height * zoom_factor))
        # Resize the image using the new size
        resized_image = pil_image.resize(new_size, Image.ANTIALIAS)
        # Convert the resized image to a PhotoImage object and update the display
        self.photo_image = ImageTk.PhotoImage(resized_image)
        self.canvas.itemconfig(self.canvas_image, image=self.photo_image)

    
    def toggle_pause(self):
        self.is_playing = not self.is_playing
        self.pause_button.config(text='Resume' if not self.is_playing else 'Pause')
        if self.is_playing:
            self.update_gif(Image.open(self.image_list[self.current_image_index]))

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        self.image_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                           if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(('.gif', '.jpg', '.jpeg', '.png'))]
        self.current_image_index = 0
        self.show_current_image()

    def show_current_image(self):
        if not self.image_list:
            return
        
        image_path = self.image_list[self.current_image_index]
        pil_image = Image.open(image_path)
        img_name=os.path.basename(image_path)
        img_name=img_name.split('.')[0]
        self.image_labels.setdefault(img_name, "None")

        # 更新文件名标签
        self.filename_label.config(text=img_name)

        self.level_var.set(self.image_labels[img_name])
        self.level_var.set("None")
        self.update_label()
        if image_path.lower().endswith('.gif'):
            self.photo_image = ImageTk.PhotoImage(pil_image)
            self.canvas.delete("all")
            self.canvas_image = self.canvas.create_image(300, 200, image=self.photo_image)
            self.update_gif(pil_image)
        else:
            pil_image = pil_image.resize((500, 500), Image.ANTIALIAS)
            self.photo_image = ImageTk.PhotoImage(pil_image)
            self.canvas.delete("all")
            self.canvas_image = self.canvas.create_image(300, 200, image=self.photo_image)

    def update_label(self):
        if self.image_list:
            image_path = self.image_list[self.current_image_index]
            img_name=os.path.basename(image_path)
            img_name=img_name.split('.')[0]
            self.image_labels[img_name] = self.level_var.get()

    def write_labels_to_csv(self):
        current_time = datetime.now()
        date_string = current_time.strftime('%Y-%m-%d')
        filename = f"Sample_class_{date_string}.csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Image', 'Label'])
            for img_name, label in self.image_labels.items():
                writer.writerow([img_name, label])

    def update_gif(self, pil_image, additional_delay=2000):
        if not self.is_playing:
            return

        try:
            pil_image.seek(pil_image.tell() + 1)
        except EOFError:
            pil_image.seek(0)

        self.photo_image = ImageTk.PhotoImage(pil_image)
        self.canvas.itemconfig(self.canvas_image, image=self.photo_image)
        delay = pil_image.info['duration'] + additional_delay
        self.root.after(delay, self.update_gif, pil_image)

    def show_prev_image(self):
        self.update_label()
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.show_current_image()

    def show_next_image(self):
        self.update_label()
        if self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            self.show_current_image()

    def get_class_img(self):
        return  self.class_f,self.save_file_name

if __name__ == '__main__':
    root = tk.Tk()
    app = ImageLabelerApp(root)
    
    def on_close():
        app.write_labels_to_csv()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()