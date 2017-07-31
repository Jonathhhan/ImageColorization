import inspect
import os

import numpy as np
import scipy.misc
from skimage import color

from src.utils.image_utils import load_bw_images, resize_image


def get_abs_path(relative):
    script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))  # script directory
    return os.path.join(script_dir, relative)


def get_image_list(dir_path):
    image_list = os.listdir(dir_path)
    ext = [".jpg", ".JPG", ".jpeg", ".JPEG", ".png"]
    return [im for im in image_list if im.endswith(tuple(ext))]


def color_images_full(model, name, b_size=32):
    """
    reg-full
    """

    abs_file_path = get_abs_path("../../data/original")
    images = get_image_list(abs_file_path)

    # get list of images to color
    num_of_images = len(images)

    # for each batch
    for batch_n in range(num_of_images // b_size):
        # load images
        original_size_images = []
        all_images_l = np.zeros((b_size, 224, 224, 1))
        for i in range(b_size):
            # get image
            image_l = load_bw_images(os.path.join(abs_file_path, images[batch_n * b_size + i]))
            original_size_images.append(image_l)
            image_l_resized = resize_image(image_l, (224, 224))
            all_images_l[i, :, :, :] = image_l_resized[:, :, np.newaxis]

        # prepare images for a global network
        all_vgg = np.zeros((num_of_images, 224, 224, 3))
        for i in range(b_size):
            all_vgg[i, :, :, :] = np.tile(all_images_l[i], (1, 1, 1, 3))

        # color
        color_im = model.predict([all_images_l, all_vgg], batch_size=b_size)

        # save all images
        abs_save_path = get_abs_path("../../data/original/")
        for i in range(b_size):
            # to rgb
            lab_im = np.concatenate((all_images_l[i, :, :, :], color_im[i]), axis=2)
            im_rgb = color.lab2rgb(lab_im)

            # save
            scipy.misc.toimage(im_rgb, cmin=0.0, cmax=1.0).save(abs_save_path + name + images[batch_n * b_size + i])