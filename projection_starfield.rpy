init python:

    random = renpy.random
  
  
    def rectangle_displayable(colour=(255, 255, 255, 255), width=1, height=1):
        """ Create a displayable to use as a particle.
        
        Args:
            colour (tuple): RGBA for the particle.
            width (int): Width of the particle.
            height (int): Height of the particle.
        
        Returns:
            displayable
        """
        star_colour = Solid(colour)
        return Fixed(star_colour, xysize=(width, height))

 
    class ProjectionStarfield(renpy.Displayable, NoRollback):
        """ Fires a displayable from the centre of the screen outwards.
        
        Args:
            star_amount (int): Number of stars to display
            depth (int): Highest z coordinate
            perspective (float): Amount of perspective projection to use
            speed (int): How quickly the stars move off screen
            image (displayable): Visual representation of a star.
            
        Attributes:
            origin_x (int): Center x coordinate of the projection.
            origin_y (int): Center y coordinate of the projection.
            ranges (list): xy coordinates where a particle can spawn. 
            depth_ranges (list): Every possible depth. Spawning randomly picks from this list.
            transforms_amount (int): Amount of size/alpha transformations
            
        """
        def __init__(self, star_amount=128, depth=16, perspective=128.0, speed=5, image=None):            
            super(renpy.Displayable, self).__init__()
            
            self.star_amount = star_amount   
            self.depth = depth
            self.perspective = perspective
            self.speed = speed

            if image is None:
                image = rectangle_displayable(width=2, height=2)            

            self.image = renpy.easy_displayable(image)

            self.origin_x = config.screen_width * 0.5
            self.origin_y = config.screen_height * 0.5
 
            self.transforms = self.__precalculate_transforms(self.image)  
            self.transforms_amount = len(self.transforms) - 1
            
            self.stars = [self.__star_data() for x in range(self.star_amount)]
            
            self.ranges = range(-25, 25)
            # Spawning in the center of the screen is ugly
            self.ranges.remove(0)
            
            self.depth_ranges = range(1, self.depth)

            self.oldst = None
        
        def __star_data(self):
            """ Create a list with data for each star.
            
            ie: [x, y, depth, transform index]
            
            Returns:
                list: Coordinates for building a star
            """
            lower = -25
            higher = 25
            
            return [
                random.randrange(lower, higher), 
                random.randrange(lower, higher), 
                random.randrange(1, self.depth), 
                random.randrange(0, self.transforms_amount)
            ]
        
        def __precalculate_transforms(self, image):
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
        
        def visit(self):
            return self.transforms
        
        def render(self, width, height, st, at):
            if self.oldst is None:
                self.oldst = st

            lag = st - self.oldst
            self.oldst = st
                
            render = renpy.Render(0, 0)
            place = render.place
            choice = random.choice
            
            w = config.screen_width
            h = config.screen_height
            
            move = abs(lag * self.speed)
            
            ranges = self.ranges
            
            for star in self.stars:
                # Z coordinate decreases each redraw, bringing it closer to the viewer.
                star[2] -= move

                # Star becomes bigger and more visible the further down the list it goes
                star[3] += 1
                
                # The star is at maximum size/brightness, stop increasing the index
                star[3] = min(star[3], self.transforms_amount)

                # If the star hits zero depth, move it to the back of the projection with random X and Y coordinates.
                if star[2] <= 0:
                    star[0] = choice(ranges)
                    star[1] = choice(ranges)
                    star[2] = choice(self.depth_ranges)
                    star[3] = 0

                transform = self.transforms[star[3]]
                    
                # Don't place a displayable if it's going to be invisible
                if transform.alpha <= 0.0:
                    continue
                    
                # Convert the 3D coordinates to 2D using perspective projection.
                k = self.perspective / star[2]
                x = int(star[0] * k + self.origin_x)
                y = int(star[1] * k + self.origin_y)

                # Draw the star (if it's visible on screen).
                if 0 <= x < w and 0 <= y < h:
                    place(transform, x, y)

            renpy.redraw(self, 0)
            return render
