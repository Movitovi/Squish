import pygame
pygame.init()
running = 1

# Set title
pygame.display.set_caption("input test")

# Set window size
display_info = pygame.display.Info()
display_size = [display_info.current_w/2, display_info.current_h/2]
display = pygame.display.set_mode(display_size)

 # Create clock
clock = pygame.time.Clock()
tick = 60
mouse_pos = (0,0)

while running:
    
    for event in pygame.event.get():
        #print(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = 0
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYDOWN:
                key_direction = (event.type == pygame.KEYDOWN)
                print(key_direction)
    pygame.display.update()
    clock.tick(tick)
pygame.quit()