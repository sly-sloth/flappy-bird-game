import pygame

# Initialize Pygame
pygame.init()

# Set up the display
display_width = 800
display_height = 600
window = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Key Press Example')

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)

# Set up font
font = pygame.font.Font(None, 74)

# Function to display text
def display_text(text, position):
    text_surface = font.render(text, True, black)
    window.blit(text_surface, position)

# Main loop flag
running = True

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                print("The 'A' key was pressed")
            elif event.key == pygame.K_LEFT:
                print("Left arrow key was pressed")
            elif event.key == pygame.K_RIGHT:
                print("Right arrow key was pressed")
            elif event.key == pygame.K_UP:
                print("Up arrow key was pressed")
            elif event.key == pygame.K_DOWN:
                print("Down arrow key was pressed")
            elif event.key == pygame.K_SPACE:
                print("Space key was pressed")

    # Fill the background with white
    window.fill(white)

    # Display instructions
    display_text('Press arrow keys or A', (100, 250))

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
