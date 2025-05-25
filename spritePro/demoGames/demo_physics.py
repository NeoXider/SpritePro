import pygame
import pymunk
import pymunk.pygame_util
import random
import colorsys
import math

# Initialize Pygame and Pymunk
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Physics Demo - Bouncing Balls")
clock = pygame.time.Clock()

# Initialize font for text rendering
font = pygame.font.Font(None, 36)  # None uses default font, 36 is size

# Create a space (physics world)
space = pymunk.Space()
space.gravity = (0, 500)  # Set gravity
space.damping = 0.8  # Add some damping to make it more stable

# Create a ring in the center
center_x, center_y = WIDTH // 2, HEIGHT // 2
outer_radius = 250
inner_radius = 240  # Increased inner radius to make ring thinner

# Create a static body for the ring
ring_body = pymunk.Body(body_type=pymunk.Body.STATIC)
ring_body.position = (center_x, center_y)

# Create the ring shape using multiple segments
num_segments = 32  # Number of segments to create the ring
segments = []
for i in range(num_segments):
    angle1 = 2 * math.pi * i / num_segments
    angle2 = 2 * math.pi * (i + 1) / num_segments
    
    # Outer point
    x1 = outer_radius * math.cos(angle1)
    y1 = outer_radius * math.sin(angle1)
    x2 = outer_radius * math.cos(angle2)
    y2 = outer_radius * math.sin(angle2)
    
    # Inner point
    x3 = inner_radius * math.cos(angle2)
    y3 = inner_radius * math.sin(angle2)
    x4 = inner_radius * math.cos(angle1)
    y4 = inner_radius * math.sin(angle1)
    
    # Create two triangles for each segment
    vertices1 = [(x1, y1), (x2, y2), (x3, y3)]
    vertices2 = [(x1, y1), (x3, y3), (x4, y4)]
    
    # Create shapes for both triangles
    shape1 = pymunk.Poly(ring_body, vertices1)
    shape2 = pymunk.Poly(ring_body, vertices2)
    
    # Set properties for both shapes
    for shape in [shape1, shape2]:
        shape.friction = 0.7
        shape.elasticity = 1.0  # Perfect bounce
        shape.color = (200, 200, 200, 255)  # Light gray color for the ring
        segments.append(shape)

# Add all segments to the space
space.add(ring_body, *segments)

# Ball configuration
NUM_BALLS = 1  # Change this number to add more balls
BALL_RADIUS = 20
MAX_VELOCITY = 700  # Reduced maximum velocity for the ball

# Create bouncing balls
def create_ball(x, y, radius, color):
    mass = 1
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = (x, y)
    
    # Add velocity limiting
    def limit_velocity(body, gravity, damping, dt):
        pymunk.Body.update_velocity(body, gravity, damping, dt)
        l = body.velocity.length
        if l > MAX_VELOCITY:
            body.velocity = body.velocity * (MAX_VELOCITY / l)
    
    body.velocity_func = limit_velocity
    
    shape = pymunk.Circle(body, radius)
    shape.friction = 0.7
    shape.elasticity = 1.5  # Super bouncy!
    shape.color = color
    
    space.add(body, shape)
    return shape

# Create ball with initial light color
initial_color = (200, 200, 255, 255)  # Light blue
ball = create_ball(center_x, center_y, BALL_RADIUS, initial_color)

# Background color (dark)
bg_color = (20, 20, 30)  # Dark blue-gray

# Collision handler to change ball color
def change_ball_color(arbiter, space, data):
    # Generate a new random light color using HSV
    h = random.random()
    s = 0.2 + random.random() * 0.3  # 0.2 to 0.5 for pastel colors
    v = 0.8 + random.random() * 0.2  # 0.8 to 1.0 for light colors
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    new_color = (int(r * 255), int(g * 255), int(b * 255), 255)
    
    # Update ball color
    for shape in arbiter.shapes:
        if isinstance(shape, pymunk.Circle):
            shape.color = new_color
    return True

# Add collision handler
handler = space.add_collision_handler(0, 0)  # 0 is the default collision type
handler.separate = change_ball_color

# Draw options
draw_options = pymunk.pygame_util.DrawOptions(screen)

def draw_ring():
    # Draw the ring using pygame
    pygame.draw.circle(screen, (200, 200, 200), (center_x, center_y), outer_radius, 2)
    pygame.draw.circle(screen, (200, 200, 200), (center_x, center_y), inner_radius, 2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Clear screen with current background color
    screen.fill(bg_color)
    
    # Draw the ring
    draw_ring()
    
    # Draw the physics objects
    space.debug_draw(draw_options)
    
    # Calculate and display velocity
    velocity = ball.body.velocity
    speed = math.sqrt(velocity.x**2 + velocity.y**2)
    velocity_text = f"Speed: {speed:.1f}"
    text_surface = font.render(velocity_text, True, (200, 200, 200))  # Light gray color
    screen.blit(text_surface, (10, 10))  # Position in top-left corner
    
    # Update physics
    space.step(1/60.0)
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit() 