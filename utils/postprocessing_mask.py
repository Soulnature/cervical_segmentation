import os
import numpy as np
import SimpleITK as sitk
import imageio
import cv2
from scipy.ndimage import label
def load_itk_all(filename):

    itkimage = sitk.ReadImage(filename)
    ct_scan = sitk.GetArrayFromImage(itkimage)
    return ct_scan,itkimage
def  save_itk_img(filename,imag_array,img):
    processed_image  = sitk.GetImageFromArray(imag_array)

    original_spacing = img.GetSpacing()
    original_size = img.GetSize()
    original_direction = img.GetDirection()
    original_origin = img.GetOrigin()

    new_spacing = [original_spacing[0], original_spacing[1], original_spacing[2] * (original_size[2] / imag_array.shape[0])]

    # set the postion information
    processed_image.SetSpacing(new_spacing)
    processed_image.SetDirection(original_direction)
    processed_image.SetOrigin(original_origin)
    sitk.WriteImage(processed_image, filename)

def post_deal_mask(mask_m,area_threshold):
    mask_m_=deal_multi_label(mask_m)
    mask_m_=remove_small_nosie_lebel(mask_m_,area_threshold)
    return mask_m_


def deal_multi_label(matrix):
    # Binarize the matrix: convert non-zero values to 1
    binary_matrix = (matrix > 0).astype(int)
    # Find connected components
    labeled_array, num_features = label(binary_matrix)
    matrix = np.where(labeled_array > 0, matrix, 0)
    # Iterate over each connected component to count the label values
    # and set the values within the entire connected component to the most frequent label
    for i in range(1, num_features + 1):
        # Find the coordinates that belong to the current connected component
        coordinates = np.argwhere(labeled_array == i)
        # Get the values at these coordinates in the original matrix
        labels_in_region = matrix[tuple(coordinates.T)]
        # Count the frequency of these values
        label_counts = np.bincount(labels_in_region)
        # Find the most frequent label (excluding 0 as bincount's index 0 represents the count of value 0)
        most_frequent_label = label_counts[1:].argmax() + 1
        # Update the values within the connected component to the most frequent label
        for coord in coordinates:
            matrix[tuple(coord)] = most_frequent_label
    return matrix
def remove_small_nosie_lebel(matrix,area_threshold):
    # Binarize the matrix: convert non-zero values to 1
    binary_matrix = (matrix > 0).astype(int)

    # Find connected components
    labeled_array, num_features = label(binary_matrix)
    # Define the area threshold for noise
    area_threshold = 100
    # Initialize an array to hold the sizes of the connected components
    sizes = np.bincount(labeled_array.ravel())
    # Create a mask to identify the connected components that meet the criteria
    # (i.e., have an area greater than the threshold)
    mask_sizes = sizes > area_threshold
    mask_sizes[0] = 0  # Background is not a connected component
    # Mask the labeled_array to remove small connected components
    cleaned_labeled_array = mask_sizes[labeled_array]
    # Now, convert the cleaned labeled array back to the original values
    # (i.e., where there is a labeled connected component)
    cleaned_matrix = matrix * (cleaned_labeled_array > 0)
    return cleaned_matrix

def postprocessing_label_img(img_dir,mask_dir,save_dir,area_threshold):
    # list the all files
    all_files=os.listdir(img_dir)
    for i in all_files:
        img_f,img=load_itk_all(os.path.join(img_dir,i))
        mask_f,mask=load_itk_all(os.path.join(mask_dir,i))
        ###
        n_x,n_y,n_z=img_f.shape
        extracted_layer=range(int(n_x/2-2),int(n_x/2+3))
        # extrat the medium layers #
        mask_m=mask_f[extracted_layer,::]
        imag_m=img_f[extracted_layer,::]
        ## deal the mask #
        for i in range(mask_m.shape[0]):
            mask_m[i,::]=post_deal_mask(mask_m[i,::],area_threshold)
    # save the files in outputdir ##
    save_itk_img(os.path.join(save_dir,'images/'+i),mask_m,mask)
    save_itk_img(os.path.join(save_dir,'labels/'+i),imag_m,img)