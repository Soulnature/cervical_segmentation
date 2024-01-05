# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 21:55:40 2023

@author: 1
"""
import os
import numpy as np
import SimpleITK as sitk
import imageio
import cv2

colors = {
    1: (255, 0, 0),  # 红色
    2: (0, 255, 0),  # 绿色
    3: (0, 0, 255),  # 蓝色
    4: (255, 255, 0),  # 黄色
    6: (255, 0, 255)  # 粉色
}


def load_itk_all(filename):
    itkimage = sitk.ReadImage(filename)
    ct_scan = sitk.GetArrayFromImage(itkimage)
    return ct_scan


def create_gif(img, gif_name, slice_num):
    frames = []
    for i in range(slice_num):
        frames.append(img[i, :, :])
    # Save images as frames into a gif
    imageio.mimsave(gif_name, frames, 'GIF', duration=2)
    return


def norm_z_score(img):
    # 正则化到0-1之间
    mean = np.mean(img)
    std = np.std(img)
    img = (img - mean) / (std + 0.00001)
    maxx = np.max(img)
    minn = np.min(img)
    img = (img - minn) / (maxx - minn + 0.00001)
    return img


def generater(img_folder, label_folder, save_path):
    files_1 = os.listdir(img_folder)  # 文件夹下所有目录的列表
    for j in files_1:
        file_tem = j.split('.')[0]
        imgPaths_dyn = img_folder + '/' + file_tem + '.nii.gz'
        imgPaths_mask = label_folder + '/' + file_tem + '.nii.gz'
        if os.path.isfile(imgPaths_dyn):

            img_dyn = load_itk_all(imgPaths_dyn)
            img_mask = load_itk_all(imgPaths_mask)
            img_dyn = np.flipud(np.fliplr(img_dyn))
            img_mask = np.flipud(np.fliplr(img_mask))
            img_dyn = norm_z_score(img_dyn)

            data_x = []

            for i in range(img_dyn.shape[0]):
                img_dyn_i = img_dyn[i, ::]

                img_mask_i = img_mask[i, ::]

                img_dyn_i_nor = (img_dyn_i - np.min(img_dyn_i)) / (np.max(img_dyn_i) - np.min(img_dyn_i))
                img_dyn_i_nor = (img_dyn_i_nor * 255).astype(np.uint8)
                # 如果img不是灰度图像，先将其转换为灰度图像

                # 确保图像是8位的
                img_mask_i = np.uint8(img_mask_i)

                # 应用阈值或者其他边缘检测方法来获取二值图像
             #   img_dyn_i_nor = cv2.convertScaleAbs(img_dyn_i_nor, alpha=1.2, beta=5)
                contour_overlay = cv2.cvtColor(img_dyn_i_nor, cv2.COLOR_GRAY2BGR)  # 将灰度图转换为BGR颜色图像以显示彩色轮廓
                for label, color in colors.items():
                    # 创建一个mask，其中只包含当前类别的标签
                    label_mask = np.uint8(img_mask_i == label)

                    # 查找当前类别的轮廓
                    contours, _ = cv2.findContours(label_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    # 在原始彩色图像上绘制当前类别的轮廓
                    cv2.drawContours(contour_overlay, contours, -1, color, thickness=1)

                data_x.append(contour_overlay)

            data_x = np.asarray(data_x).astype(np.uint8)

            gif_name = save_path + '/' + file_tem + '.gif'
            create_gif(data_x, gif_name, img_dyn.shape[0])

            print('gif already save')
        else:
            continue


img_folder = '/data/home/zhaoxz/cervical_vertebra/cervical_vertebra/out_put_1/images'
label_folder = '/data/home/zhaoxz/cervical_vertebra/cervical_vertebra/out_put_1/labels'
save_1 = '/data/home/zhaoxz/cervical_vertebra/batch_1_predicted'
generater(img_folder, label_folder, save_1)