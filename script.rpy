init python:
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

    rect_d = rectangle_displayable(width=2, height=2)

init:
    # Simple black background to show under the stars 
    define space = Solid((0, 0, 0, 255))  

    # Create the starfield displayables. Optional keyword arguments can tweak the default display.
    $starfield = ProjectionStarfield(rect_d, amount=128, depth=16, perspective=128.0, speed=5)

    # Create another with an image used.
    image star:
        "Star Filled-48.png"
        zoom 0.5
        #linear 2.0 rotate 360
        #repeat

    $i_starfield = ProjectionStarfield("star", amount=128, depth=16, perspective=128.0, speed=5)       
 
# Screens where the displayables are shown 
screen starfield:
    add space
    add starfield

screen starfield_with_image:
    add space
    add i_starfield
 
# The game starts here.
label start:

    show screen starfield
    
    "Space."
    
    "The final frontier."

    "These are the voyages of the starship Enterprise."

    hide screen starfield
    show screen starfield_with_image

    "It's continuing mission, to explore strange new worlds."
    return