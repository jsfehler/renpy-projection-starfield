"""renpy
init python:
"""


random = renpy.random
choice = random.choice


class Star:
    """A single item in the starfield.
    
    Attributes:
        x (int): x coordinate
        y (int): y coordinate
        z (int): z coordinate
        transform_index (int): transform index
    """
    def __init__(self, x: int, y: int, z: int, transform_index: int) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.transform_index = transform_index


class ProjectionStarfield(renpy.Displayable, NoRollback):
    """Fires a displayable from the centre of the screen outwards.
    
    Args:
        image (str|displayable): Visual representation of a star.
        amount (int): Number of stars to display
        depth (int): Highest z coordinate
        perspective (float): Amount of perspective projection to use
        speed (int): How quickly the stars move off screen

    Attributes:
        origin_x (int): Center x coordinate of the projection.
        origin_y (int): Center y coordinate of the projection.
        ranges (list): xy coordinates where a particle can spawn. 
        depth_ranges (list): Every possible depth. Spawning randomly picks from this list.
        transforms_amount (int): Amount of size/alpha transformations
    """
    def __init__(self, image, amount=128, depth=16, perspective=128.0, speed=5):            
        super(renpy.Displayable, self).__init__()
        
        self.amount = amount   
        self.depth = depth
        self.perspective = perspective
        self.speed = speed         

        self.image = renpy.easy_displayable(image)

        self.origin_x = config.screen_width * 0.5
        self.origin_y = config.screen_height * 0.5

        self.transforms = self.__precalculate_transforms(self.image)  
        self.transforms_amount = len(self.transforms) - 1

        # Use random values to populate the starfield.
        self.ranges = range(-25, 25)
        # Spawning in the center of the screen is ugly
        self.ranges.remove(0)

        self.depth_ranges = range(1, self.depth)

        self.stars = [
            Star(
                x=choice(self.ranges),
                y=choice(self.ranges), 
                z=choice(self.depth_ranges),
                transform_index=random.randrange(0, self.transforms_amount),
            ) for _ in range(self.amount)
        ]

        self.oldst = None
    
    def __precalculate_transforms(self, image) -> list[Transform]:
        """
        Pre-calculate all the size/alpha transforms that are possible 
        so they don't have to be recreated in render() every single frame.
        
        Returns:
            list: Displayables for every possible size/alpha
        """
        # All possible depths. Start from maximum depth and decrease
        current_depth = float(self.depth)
        all_depths = []
        step = 0.09

        while current_depth > 0:
            all_depths.append(current_depth)
            current_depth -= step

        # All possible transform factors
        # Using Linear Interpolation, make distant stars smaller and darker than closer stars.            
        t_factors = [(1 - float(d) / self.depth) * 2 for d in all_depths]
    
        # Create list with a Transform() for every possible star
        return [
            (Transform(child=image, zoom=item, alpha=item)) for item in t_factors
        ]      
    
    def _reset_star(self, star: Star) -> None:
        star.x = choice(self.ranges)
        star.y = choice(self.ranges)
        star.z = choice(self.depth_ranges)
        star.transform_index = 0
    
    def perspective_projection(self, star: Star) -> tuple[int, int]:
        # Convert the 3D coordinates to 2D using perspective projection.
        factor = self.perspective / star.z
        x = int(star.x * factor) + self.origin_x
        y = int(star.y * factor) + self.origin_y

        return (x, y)

    def visit(self):
        return self.transforms

    def render(self, width, height, st, at):
        if self.oldst is None:
            self.oldst = st

        delta_time = st - self.oldst
        self.oldst = st
            
        w = config.screen_width
        h = config.screen_height

        render = renpy.Render(0, 0)
        place = render.place
        
        move = abs(delta_time * self.speed)
        
        for star in self.stars:
            # Z coordinate decreases each redraw, bringing it closer to the viewer.
            star.z -= move

            # Star becomes bigger and more visible the further down the list it goes
            star.transform_index += 1

            # The star is at maximum size/brightness, stop increasing the index
            star.transform_index = min(star.transform_index, self.transforms_amount)

            # If the star hits zero depth, move it to the back of the projection with random X and Y coordinates.
            if star.z <= 0:
                self._reset_star(star)

            transform = self.transforms[star.transform_index]

            # Don't place a displayable if it's going to be invisible
            if transform.alpha <= 0.0:
                continue

            x, y = self.perspective_projection(star)

            # Draw the star (if it's visible on screen).
            if 0 <= x < w and 0 <= y < h:
                place(transform, x, y)

        renpy.redraw(self, 0)
        return render
