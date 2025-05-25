import pygame
import pymunk
import pymunk.pygame_util

# Initialize Pygame and Pymunk
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()

# Create a space (physics world)
space = pymunk.Space()
space.gravity = (0, 900)  # Set gravity

# Create a static body (ground)
ground = pymunk.Segment(space.static_body, (0, 500), (600, 500), 2)
ground.friction = 0.7
space.add(ground)

# Create a dynamic body (ball)
ball_mass = 1
ball_radius = 25
ball_moment = pymunk.moment_for_circle(ball_mass, 0, ball_radius)
ball_body = pymunk.Body(ball_mass, ball_moment)
ball_body.position = (300, 100)
ball_shape = pymunk.Circle(ball_body, ball_radius)
ball_shape.friction = 0.7
space.add(ball_body, ball_shape)

# Draw options
draw_options = pymunk.pygame_util.DrawOptions(screen)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    screen.fill((255, 255, 255))
    
    # Draw everything
    space.debug_draw(draw_options)
    
    # Update physics
    space.step(1/60.0)
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()