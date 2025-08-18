import pygame
import math
pygame.init()

# Load both images
background = pygame.image.load("Simulation-Software/data/test/Harbor1.png")
depth_map = pygame.image.load("Simulation-Software/data/test/Harbor1_DepthMap.png")
icon = pygame.image.load("Simulation-Software/data/test/icon.png")

screen = pygame.display.set_mode((737, 535))
width, height = screen.get_size()
background_scaled = pygame.transform.scale(background, (width, height))
depth_map_scaled = pygame.transform.scale(depth_map, (width, height))
pygame.display.set_icon(icon)

# Map colors (R, G, B) → depth labels
DEPTH_CATEGORIES = {
    (255, 114, 0): "Land",         # Orange
    (0, 229, 255): "Shallow: <10ft", # Light Blue
    (10, 63, 255): "Medium: <20ft",   # Deep Blue
    (120, 43, 255): "Deep: 20+ ft"   # Purple
}

COLOR_TOLERANCE = 30  # How close a color can be and still count as a match

def closest_depth(rgb):
    """Return the depth category for the closest matching color."""
    min_dist = float('inf')
    closest = "Unknown"
    for ref_rgb, category in DEPTH_CATEGORIES.items():
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, ref_rgb)))
        if dist < min_dist and dist <= COLOR_TOLERANCE:
            min_dist = dist
            closest = category
    return closest

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Get mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Get color from depth map
    color = depth_map_scaled.get_at((mouse_x, mouse_y))[:3]  # Ignore alpha

    # Get closest match
    depth = closest_depth(color)

    print(f"Depth at ({mouse_x}, {mouse_y}): {depth}")

    # Draw background
    screen.blit(background_scaled, (0, 0))
    pygame.display.set_caption("Active Simulation")
    pygame.display.flip()

pygame.quit()