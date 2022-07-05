import pygame

refresh_rate = 30. # refresh rate of the monitor
 
pygame.init()
# screen = pygame.display.set_mode((400,400))
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)
 
 
def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("coral"))
    return fps_text
 
 
running = True
while running:
    clock.tick(refresh_rate)
    screen.fill((0, 0, 0))
    screen.blit(update_fps(), (10,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False  # Set running to False to end the while loop.
    clock.tick(60)
    pygame.display.update()
 
pygame.quit()