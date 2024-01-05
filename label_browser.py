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
        #self.save_file_name=[]
       # self.class_f=[]
        self.img_name=None
        # 图像列表和当前索引
        self.image_list = []
        self.current_image_index = 0
        self.is_playing = True
        self.image_labels = {}
        # 左侧的Frame用于放置图像和导航按钮
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side='left')

        # Open folder button
        self.open_button = tk.Button(self.left_frame, text='Open folder', command=self.open_folder)
        self.open_button.pack()

        # 图像画布
        self.canvas = tk.Canvas(self.left_frame, width=600, height=400, bg='grey')
        self.canvas.pack()
        self.navigation_frame = tk.Frame(self.left_frame)
        self.navigation_frame.pack()
        self.prev_button = tk.Button(self.navigation_frame, text='Prev.', command=self.show_prev_image)
        self.prev_button.pack(side='left')

        # 添加一个暂停/继续按钮并使其居中
        self.pause_button = tk.Button(self.navigation_frame, text='Pause', command=self.toggle_pause)
        self.pause_button.pack(side='left', padx=10)  # padx增加一些水平间距

        self.next_button = tk.Button(self.navigation_frame, text='Next', command=self.show_next_image)
        self.next_button.pack(side='left')

        # 右侧的Frame用于放置等级单选按钮和标签
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side='right', fill='y')

        # “Label Selection”标签
        self.label_selection_label = tk.Label(self.right_frame, text="Label Selection")
        self.label_selection_label.pack()

        # 等级单选按钮
        self.level_var = tk.StringVar()
        self.level_var.set("None")  # 设置默认值

        self.levels = ["Grade 0", "Grade 1", "Grade 2", "Grade 3", "Grade 4"]
        self.radio_buttons = []
        for level in self.levels:
            rb = tk.Radiobutton(self.right_frame, text=level, variable=self.level_var, value=level)
            rb.pack(anchor='w')
            self.radio_buttons.append(rb)
        #self.radio_buttons.config(command=self.update_label)
    def toggle_pause(self):
        self.is_playing = not self.is_playing
        # 更新按钮的文本
        self.pause_button.config(text='Resume' if not self.is_playing else 'Pause')
        # 如果切换到播放状态，则更新GIF
        if self.is_playing:
            self.update_gif(Image.open(self.image_list[self.current_image_index]))
    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        # 获取所有图像文件
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

        # 更新标签选择到当前图像的标签
        self.level_var.set(self.image_labels[img_name])
        # 清除标签选择
        self.level_var.set("None")
        self.update_label()
        # 如果是GIF，则需要特殊处理
        if image_path.lower().endswith('.gif'):
            self.photo_image = ImageTk.PhotoImage(pil_image)
            self.canvas.delete("all")  # 清除画布上之前的图像
            self.canvas_image = self.canvas.create_image(300, 200, image=self.photo_image)
            self.update_gif(pil_image)  # 更新GIF帧
        else:
            pil_image = pil_image.resize((500, 500), Image.ANTIALIAS)
            self.photo_image = ImageTk.PhotoImage(pil_image)
            self.canvas.delete("all")  # 清除画布上之前的图像
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
        #self.root.destroy()  # 关闭主窗口

    def update_gif(self, pil_image, additional_delay=2000):
        if not self.is_playing:
            return  # 如果不是播放状态，则不更新到下一帧

        try:
            # 尝试移动到下一帧
            pil_image.seek(pil_image.tell() + 1)
        except EOFError:
            # 如果是最后一帧，就从头开始
            pil_image.seek(0)

        self.photo_image = ImageTk.PhotoImage(pil_image)
        self.canvas.itemconfig(self.canvas_image, image=self.photo_image)
        # 获取GIF帧的持续时间并增加额外的延迟
        delay = pil_image.info['duration'] + additional_delay
        self.root.after(delay, self.update_gif, pil_image)


    def show_prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.show_current_image()

    def show_next_image(self):
        self.update_label()
        if self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            self.show_current_image()

    def show_prev_image(self):
        self.update_label()
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.show_current_image()
    def get_class_img(self):
        return  self.class_f,self.save_file_name

if __name__ == '__main__':
    root = tk.Tk()
    app = ImageLabelerApp(root)
    
    # 在程序关闭前更新标签并写入CSV文件，然后销毁窗口
    def on_close():
        app.write_labels_to_csv()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()