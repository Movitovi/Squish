import pygame
pygame.init()
screen = pygame.display.set_mode((320,320))
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done=True

        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        if event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

    screen.fill(0xaaaaaa)
    

    joystick_count = pygame.joystick.get_count()

    print("Number of joysticks: {}".format(joystick_count) )
    

    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        print("Joystick {}".format(i) )
        

        name = joystick.get_name()
        print("Joystick name: {}".format(name) )

        axes = joystick.get_numaxes()
        print("Number of axes: {}".format(axes) )
        

        for i in range( axes ):
            axis = joystick.get_axis( i )
            print("Axis {} value: {:>6.0f}".format(i, axis) )
        

        buttons = joystick.get_numbuttons()
        print( "Number of buttons: {}".format(buttons) )
        

        for i in range( buttons ):
            button = joystick.get_button( i )
            print("Button {:>2} value: {}".format(i,button) )
        

        hats = joystick.get_numhats()
        print("Number of hats: {}".format(hats) )
        

        for i in range( hats ):
            hat = joystick.get_hat( i )
            print( "Hat {} value: {}".format(i, str(hat)) )
        

    pygame.display.flip()
    pygame.time.Clock().tick(0.2)
