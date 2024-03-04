from consts import GRID_WIDTH, GRID_HEIGHT

def is_valid_position(center_x: int, center_y: int):
    """Checks if given position is within bounds

    Inputs
    ------
    center_x (int): x-coordinate
    center_y (int): y-coordinate

    Returns
    -------
    bool: True if valid, False otherwise
    """
    return center_x > 0 and center_y > 0 and center_x < GRID_WIDTH - 1 and center_y < GRID_HEIGHT - 1