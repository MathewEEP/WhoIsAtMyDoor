import cv2
import os
import sys
import random
import argparse
import numpy as np
from PIL import Image, ImageFile

folder_path = "/images/not_masked"


__version__ = '0.3.0'

IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
DEFAULT_IMAGE_PATH = os.path.join(IMAGE_DIR, 'default-mask.png')
BLACK_IMAGE_PATH = os.path.join(IMAGE_DIR, 'black-mask.png')
BLUE_IMAGE_PATH = os.path.join(IMAGE_DIR, 'blue-mask.png')
RED_IMAGE_PATH = os.path.join(IMAGE_DIR, 'red-mask.png')


def cli():
    parser = argparse.ArgumentParser(description='Wear a face mask in the given picture.')
    parser.add_argument('pic_path', help='Picture path.')
    parser.add_argument('--show', action='store_true', help='Whether show picture with mask or not.')
    parser.add_argument('--model', default='hog', choices=['hog', 'cnn'], help='Which face detection model to use.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--black', action='store_true', help='Wear black mask')
    group.add_argument('--blue', action='store_true', help='Wear blue mask')
    group.add_argument('--red', action='store_true', help='Wear red mask')
    args = parser.parse_args()

    pic_path = args.pic_path
    if not os.path.exists(args.pic_path):
        print(f'Picture {pic_path} not exists.')
        sys.exit(1)

    if args.black:
        mask_path = BLACK_IMAGE_PATH
    elif args.blue:
        mask_path = BLUE_IMAGE_PATH
    elif args.red:
        mask_path = RED_IMAGE_PATH
    else:
        mask_path = DEFAULT_IMAGE_PATH

    FaceMasker(pic_path, mask_path, args.show, args.model).mask()

def create_mask(image_path):
    pic_path = image_path
    mask_path = "/Users/mattsmacbook/Desktop/Projects/Security/Who-Is-At-My-Door-v0.0.3/images/mask.png"
    show = False
    model = "hog"
    FaceMasker(pic_path, mask_path, show, model).mask()


class FaceMasker:
    KEY_FACIAL_FEATURES = ('nose_bridge', 'chin')

    def __init__(self, face_path, mask_path, show=False, model='hog'):
        self.face_path = face_path
        self.mask_path = mask_path
        self.show = show
        self.model = model
        self._face_img: ImageFile = None
        self._mask_img: ImageFile = None
        self.face_location = None
        self.face_landmarks = None

    def mask(self):
        import face_recognition

        face_image_np = face_recognition.load_image_file(self.face_path)
        self.face_location = face_recognition.face_locations(face_image_np, model=self.model)
        self.face_landmarks = face_recognition.face_landmarks(face_image_np, self.face_location)
        self._face_img = Image.fromarray(face_image_np)
        self._mask_img = Image.open(self.mask_path)

        found_face = False
        for face_landmark in self.face_landmarks:
            # check whether facial features meet requirement
            skip = False
            for facial_feature in self.KEY_FACIAL_FEATURES:
                if facial_feature not in face_landmark:
                    skip = True
                    break
            if skip:
                continue

            # mask face
            found_face = True
            self._mask_face(face_landmark)

        if found_face:
            if self.show:
                self._face_img.show()

            # save
            # self._save()
        else:
            print('Found no face.')

    def _mask_face(self, face_landmark: dict):
        image = cv2.imread(self.face_path, cv2.IMREAD_COLOR)
        top_left = (self.face_location[0][3], self.face_location[0][0])
        bottom_right = (self.face_location[0][1], self.face_location[0][2])
        image2 = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        height, width, c = image2.shape
        im_pil = Image.fromarray(image2).convert("RGBA")
        image = Image.fromarray(image).convert("RGBA")
        self._mask_img = self._mask_img.resize((height, width))
        im_pil.paste(self._mask_img, (0, 0), self._mask_img)
        image.paste(im_pil, (top_left[0], top_left[1]), im_pil)
        path_splits = os.path.splitext(self.face_path)
        new_face_path = "/Users/mattsmacbook/Desktop/Projects/Security/Who-Is-At-My-Door-v0.0.3/images/masked/" + path_splits[0].split("/")[-1] + '-with-mask' + ".png"
        image.save(new_face_path)

    def _save(self):
        path_splits = os.path.splitext(self.face_path)
        new_face_path = path_splits[0] + '-with-mask' + path_splits[1]
        self._face_img.save(new_face_path)
        print(f'Save to {new_face_path}')

    @staticmethod
    def get_distance_from_point_to_line(point, line_point1, line_point2):
        distance = np.abs((line_point2[1] - line_point1[1]) * point[0] +
                          (line_point1[0] - line_point2[0]) * point[1] +
                          (line_point2[0] - line_point1[0]) * line_point1[1] +
                          (line_point1[1] - line_point2[1]) * line_point1[0]) / \
                   np.sqrt((line_point2[1] - line_point1[1]) * (line_point2[1] - line_point1[1]) +
                           (line_point1[0] - line_point2[0]) * (line_point1[0] - line_point2[0]))
        return int(distance)


images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
for i in range(len(images)):
    print("the path of the image is", images[i])
    #image = cv2.imread(images[i])
    #c = c + 1
    create_mask(images[i])
