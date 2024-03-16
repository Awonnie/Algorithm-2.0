from PIL import Image
import glob
import os
import time
from direction import Direction


def stitch_raw_imgs():
    """
    Stitches the images in the folder together and saves it into images/stitched folder
    """
    # Initialize paths
    img_folder = 'images/raw'
    img_path = glob.glob(os.path.join(img_folder, "*.jpg"))
    stitch_folder = "images/stitched"
    stitch_path = os.path.join(stitch_folder, f'stitched-{int(time.time())}.jpg') 

    # Open all images
    images = [Image.open(x) for x in img_path]

    # Get the width and height of each image
    width, height = zip(*(i.size for i in images))

    # Calculate the total width and max height of the stitched image, as we are stitching horizontally
    total_width = sum(width)
    max_height = max(height)
    stitch_img = Image.new('RGB', (total_width, max_height))
    x_offset = 0

    # Stitch the images together
    for img in images:
        stitch_img.paste(img, (x_offset, 0))
        x_offset += img.size[0]

    # Save the stitched image to the path
    stitch_img.save(stitch_path)

    return stitch_img

def stitch_annotated_imgs():
    """
    Stitches the images in the folder together and saves it into stitched folder

    Basically similar to stitch_image() but with different folder names and slightly different drawing of bounding boxes and text
    """
    stitch_folder = 'images/stitched'
    stitch_path = os.path.join(stitch_folder, f'stitched-{int(time.time())}.jpeg')

    annotated_img_folder = 'images/annotated'
    annotated_path = glob.glob(os.path.join(annotated_img_folder+"/annotated_image_*.jpg"))
    annotated_timestamps = [img_path.split("_")[-1][:-4] for img_path in annotated_path]
    
    sorted_annotated = sorted(zip(annotated_path, annotated_timestamps), key=lambda x: x[1])

    annotated_imgs = [Image.open(x[0]) for x in sorted_annotated]
    width, height = zip(*(i.size for i in annotated_imgs))
    total_width = sum(width)
    max_height = max(height)
    stitch_img = Image.new('RGB', (total_width, max_height))
    x_offset = 0

    for img in annotated_imgs:
        stitch_img.paste(img, (x_offset, 0))
        x_offset += img.size[0]
    stitch_img.save(stitch_path)

    return stitch_img

def clear_images():
    for filename in os.listdir('images/raw'):
        if filename.endswith(".jpg"):
            file_path = os.path.join('images/raw',filename)
            os.remove(file_path)

    for filename in os.listdir('images/annotated'):
        if filename.endswith(".jpg"):
            file_path = os.path.join('images/annotated',filename)
            os.remove(file_path)

    for filename in os.listdir('images/stitched'):
        if filename.startswith("stitched"):
            file_path = os.path.join('images/stitched',filename)
            os.remove(file_path)


def setup_img_folders():
    try:
        os.makedirs('images/raw', exist_ok=True)
        os.makedirs('images/annotated', exist_ok=True)
        os.makedirs('images/stitched', exist_ok=True)
    except OSError as error:
        print(error)

def get_extended_path(path):
    extended_path = []
    for i in range(len(path)):

        extended_path.append(path[i].get_dict())

        if(i+1 == len(path)): 
            break

        cur_step = path[i]
        next_step = path[i+1]
        if cur_step.direction == next_step.direction:
            continue

        # Add the intermediate steps for different turns
        x_change = next_step.x - cur_step.x
        y_change = next_step.y - cur_step.y
        intermediate_path = []
        if cur_step.direction == Direction.NORTH and next_step.direction == Direction.EAST:
            #FR
            if x_change > 0:
                intermediate_path = [
                    {'x':cur_step.x, 'y':cur_step.y + 1, 'd':Direction.NORTH, 's':-1},
                    {'x':cur_step.x, 'y':cur_step.y + 2, 'd':Direction.NORTH, 's':-1},
                    {'x':cur_step.x + 1, 'y':cur_step.y + 2, 'd':Direction.EAST, 's':-1},
                    ]
            #BL
            else:
                intermediate_path = [
                    {'x':cur_step.x, 'y':cur_step.y - 1, 'd':Direction.NORTH, 's':-1},
                    {'x':cur_step.x, 'y':cur_step.y - 2, 'd':Direction.NORTH, 's':-1},
                    {'x':cur_step.x - 1, 'y':cur_step.y - 2, 'd':Direction.EAST, 's':-1},
                    ]
        elif cur_step.direction == Direction.NORTH and next_step.direction == Direction.WEST:
            #FL
            if x_change < 0:
                intermediate_path = [
                    {'x':cur_step.x, 'y':cur_step.y + 1, 'd':Direction.NORTH, 's':-1},
                    {'x':cur_step.x, 'y':cur_step.y + 2, 'd':Direction.NORTH, 's':-1},
                    {'x':cur_step.x - 1, 'y':cur_step.y + 2, 'd':Direction.WEST, 's':-1},
                    ]
            #BR
            else:
                intermediate_path = [
                    {'x':cur_step.x, 'y':cur_step.y - 1, 'd':Direction.NORTH, 's':-1},
                    {'x':cur_step.x, 'y':cur_step.y - 2, 'd':Direction.NORTH, 's':-1},
                    {'x':cur_step.x + 1, 'y':cur_step.y - 2, 'd':Direction.WEST, 's':-1},
                    ]
        elif cur_step.direction == Direction.EAST and next_step.direction == Direction.NORTH:
            #FL
            if y_change > 0:
                intermediate_path = [
                    {'x':cur_step.x + 1, 'y':cur_step.y, 'd':Direction.EAST, 's':-1},
                    {'x':cur_step.x + 2, 'y':cur_step.y, 'd':Direction.EAST, 's':-1},
                    {'x':cur_step.x + 2, 'y':cur_step.y + 1, 'd':Direction.NORTH, 's':-1},
                    ]
            #BR
            else:
                intermediate_path = [
                    {'x':cur_step.x - 1, 'y':cur_step.y, 'd':Direction.EAST, 's':-1},
                    {'x':cur_step.x - 2, 'y':cur_step.y, 'd':Direction.EAST, 's':-1},
                    {'x':cur_step.x - 2, 'y':cur_step.y - 1, 'd':Direction.NORTH, 's':-1},
                    ]
        elif cur_step.direction == Direction.EAST and next_step.direction == Direction.SOUTH:
            #FR
            if y_change < 0:
                intermediate_path = [
                    {'x':cur_step.x + 1, 'y':cur_step.y, 'd':Direction.EAST, 's':-1},
                    {'x':cur_step.x + 2, 'y':cur_step.y, 'd':Direction.EAST, 's':-1},
                    {'x':cur_step.x + 2, 'y':cur_step.y - 1, 'd':Direction.SOUTH, 's':-1},
                    ]
            #BL
            else:
                intermediate_path = [
                    {'x':cur_step.x - 1, 'y':cur_step.y, 'd':Direction.EAST, 's':-1},
                    {'x':cur_step.x - 2, 'y':cur_step.y, 'd':Direction.EAST, 's':-1},
                    {'x':cur_step.x - 2, 'y':cur_step.y - 1, 'd':Direction.SOUTH, 's':-1},
                    ]
        elif cur_step.direction == Direction.WEST and next_step.direction == Direction.SOUTH:
            #FL
            if y_change < 0:
                intermediate_path = [
                    {'x':cur_step.x - 1, 'y':cur_step.y, 'd':Direction.WEST, 's':-1},
                    {'x':cur_step.x - 2, 'y':cur_step.y, 'd':Direction.WEST, 's':-1},
                    {'x':cur_step.x - 2, 'y':cur_step.y - 1, 'd':Direction.SOUTH, 's':-1},
                    ]
            #BR
            else:
                intermediate_path = [
                    {'x':cur_step.x + 1, 'y':cur_step.y, 'd':Direction.WEST, 's':-1},
                    {'x':cur_step.x + 2, 'y':cur_step.y, 'd':Direction.WEST, 's':-1},
                    {'x':cur_step.x + 2, 'y':cur_step.y + 1, 'd':Direction.SOUTH, 's':-1},
                    ]
        elif cur_step.direction == Direction.WEST and next_step.direction == Direction.NORTH:
            #FR
            if y_change > 0:
                intermediate_path = [
                    {'x':cur_step.x - 1, 'y':cur_step.y, 'd':Direction.WEST, 's':-1},
                    {'x':cur_step.x - 2, 'y':cur_step.y, 'd':Direction.WEST, 's':-1},
                    {'x':cur_step.x - 2, 'y':cur_step.y + 1, 'd':Direction.NORTH, 's':-1},
                    ]
            #BL
            else:
                intermediate_path = [
                    {'x':cur_step.x + 1, 'y':cur_step.y, 'd':Direction.WEST, 's':-1},
                    {'x':cur_step.x + 2, 'y':cur_step.y, 'd':Direction.WEST, 's':-1},
                    {'x':cur_step.x + 2, 'y':cur_step.y - 1, 'd':Direction.NORTH, 's':-1},
                    ]
        elif cur_step.direction == Direction.SOUTH and next_step.direction == Direction.EAST:
            #FL
            if x_change > 0:
                intermediate_path = [
                    {'x':cur_step.x, 'y':cur_step.y - 1, 'd':Direction.SOUTH, 's':-1},
                    {'x':cur_step.x, 'y':cur_step.y - 2, 'd':Direction.SOUTH, 's':-1},
                    {'x':cur_step.x + 1, 'y':cur_step.y - 2, 'd':Direction.EAST, 's':-1},
                    ]
            #BR
            else:
                intermediate_path = [
                    {'x':cur_step.x, 'y':cur_step.y + 1, 'd':Direction.SOUTH, 's':-1},
                    {'x':cur_step.x, 'y':cur_step.y + 2, 'd':Direction.SOUTH, 's':-1},
                    {'x':cur_step.x - 1, 'y':cur_step.y + 2, 'd':Direction.EAST, 's':-1},
                    ]
        elif cur_step.direction == Direction.SOUTH and next_step.direction == Direction.WEST:
            #FR
            if x_change < 0:
                intermediate_path = [
                    {'x':cur_step.x, 'y':cur_step.y - 1, 'd':Direction.SOUTH, 's':-1},
                    {'x':cur_step.x, 'y':cur_step.y - 2, 'd':Direction.SOUTH, 's':-1},
                    {'x':cur_step.x - 1, 'y':cur_step.y - 2, 'd':Direction.WEST, 's':-1},
                    ]
            #BL
            else:
                intermediate_path = [
                    {'x':cur_step.x, 'y':cur_step.y + 1, 'd':Direction.SOUTH, 's':-1},
                    {'x':cur_step.x, 'y':cur_step.y + 2, 'd':Direction.SOUTH, 's':-1},
                    {'x':cur_step.x + 1, 'y':cur_step.y + 2, 'd':Direction.WEST, 's':-1},
                ]

        for to_insert in intermediate_path:
            extended_path.append(to_insert)

    return extended_path