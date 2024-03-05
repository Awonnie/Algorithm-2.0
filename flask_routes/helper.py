from PIL import Image
import glob
import os
import shutil
import time


def stitch_image():
    """
    Stitches the images in the folder together and saves it into images/stitched folder
    """
    # Initialize paths
    img_folder = 'images'
    img_path = glob.glob(os.path.join(img_folder, "*.jpg"))
    stitched_img_folder = "images/stitched"
    stitched_path = os.path.join(img_folder, f'stitched-{int(time.time())}.jpg') #changed fim jpeg to jpg

    # Open all images
    images = [Image.open(x) for x in img_path]
    # Get the width and height of each image
    width, height = zip(*(i.size for i in images))
    # Calculate the total width and max height of the stitched image, as we are stitching horizontally
    total_width = sum(width)
    max_height = max(height)
    stitchedImg = Image.new('RGB', (total_width, max_height))
    x_offset = 0

    # Stitch the images together
    for im in images:
        stitchedImg.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    # Save the stitched image to the path
    stitchedImg.save(stitched_path)

    # Move original images to "originals" subdirectory
    for img in img_path:
        shutil.move(img, os.path.join(
            "images", "raw", os.path.basename(img)))

    return stitchedImg

def stitch_image_own():
    """
    Stitches the images in the folder together and saves it into stitched folder

    Basically similar to stitch_image() but with different folder names and slightly different drawing of bounding boxes and text
    """
    imgFolder = 'stitched'
    stitchedPath = os.path.join(imgFolder, f'stitched-{int(time.time())}.jpeg')

    imgPaths = glob.glob(os.path.join(imgFolder+"/annotated_image_*.jpg"))
    imgTimestamps = [imgPath.split("_")[-1][:-4] for imgPath in imgPaths]
    
    sortedByTimeStampImages = sorted(zip(imgPaths, imgTimestamps), key=lambda x: x[1])

    images = [Image.open(x[0]) for x in sortedByTimeStampImages]
    width, height = zip(*(i.size for i in images))
    total_width = sum(width)
    max_height = max(height)
    stitchedImg = Image.new('RGB', (total_width, max_height))
    x_offset = 0

    for im in images:
        stitchedImg.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    stitchedImg.save(stitchedPath)

    return stitchedImg

def clear_images():
    for filename in os.listdir('images/raw'):
        if filename.endswith(".jpg"):
            file_path = os.path.join('images/raw',filename)
            os.remove(file_path)

    for filename in os.listdir('images/stitched'):
        if filename.endswith(".jpg"):
            file_path = os.path.join('images/stitched',filename)
            os.remove(file_path)


def setup_img_folders():
    try:
        os.makedirs('images/raw', exist_ok=True)
        os.makedirs('images/stitched', exist_ok=True)
    except OSError as error:
        print("Directory can't be created")