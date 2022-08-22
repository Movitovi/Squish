import pygame, os, time

# TODO:
# Work on the settings window next
# have player profiles that can either be
# controllers or keyboard maps
#
# Make any up control set game.up to 1
# Same for game.down, and game.select
#
# Maybe make arrows, return, space, and
# tab all default keys in menus regardless
# of player controls

class game():
    def __init__(self):
        pygame.init()
        self.running = 1
        
        file = open(os.path.join(os.getcwd(), 'settings.txt'))
        self.settings_file = file.readlines()
        file.close()
        
        pygame.display.set_caption('squish')
        self.display_info = pygame.display.Info()
        self.display_size = [self.display_info.current_w, self.display_info.current_h]
        self.display = pygame.display.set_mode(self.display_size)
        self.surface = pygame.Surface(self.display_size)
        
        self.clock = pygame.time.Clock()
        self.tick = 60
        
        self.update_joysticks()
        
        # Page variables
        self.page = 'menu'
        self.up = 0
        self.down = 0
        self.left = 0
        self.right = 0
        self.select = 0
        self.back = 0
        self.menu_input_delay_index = 0
        self.menu_input_timedelay_first = 0.5
        self.menu_input_timedelay_second = 0.1
        self.menu_input_timestamp = time.time() - self.menu_input_timedelay_first
        
        # Menu variables
        self.menu_cursor = 0
        self.menu_color = 0xbbbbbb
        self.menu_button_color = 0x888888
        self.menu_text_color = 0x000000
        self.menu_title = ['squish', self.menu_text_color, 128, 0, [self.display_size[0]/2, self.display_size[1]/5], [0, 0]]
        self.menu_buttons = []
        self.menu_buttons.append(['Play', self.menu_text_color, 32, 1, [self.display_size[0]/2-128, self.display_size[1]/2-146], [256, 64]])
        self.menu_buttons.append(['Level Editor', self.menu_text_color, 32, 1, [self.display_size[0]/2-128, self.display_size[1]/2-70], [256, 64]])
        self.menu_buttons.append(['Settings', self.menu_text_color, 32, 1, [self.display_size[0]/2-128, self.display_size[1]/2+6], [256, 64]])
        self.menu_buttons.append(['Quit', self.menu_text_color, 32, 1, [self.display_size[0]/2-128, self.display_size[1]/2+82], [256, 64]])
        
    def update_joysticks(self):
        self.joysticks = []
        for i in range(0, pygame.joystick.get_count()):
            self.joysticks.append(pygame.joystick.Joystick(i))
            self.joysticks[i].init()
    
    def get_inputs(self):
        self.mouse_moved = not ((0,0) == pygame.mouse.get_rel())
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_rmb = pygame.mouse.get_pressed()[0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = 0
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                key_direction = (event.type == pygame.KEYDOWN)
                if event.key == pygame.K_UP:
                    self.up = key_direction
                    self.menu_input_delay_index = 0
                elif event.key == pygame.K_DOWN:
                    self.down = key_direction
                    self.menu_input_delay_index = 0
                elif event.key == pygame.K_LEFT:
                    self.left = key_direction
                    self.menu_input_delay_index = 0
                elif event.key == pygame.K_RIGHT:
                    self.right = key_direction
                    self.menu_input_delay_index = 0
                elif event.key == pygame.K_RETURN:
                    self.select = key_direction
                    self.menu_input_delay_index = 0
                elif event.key == pygame.K_ESCAPE:
                    self.back = key_direction
                    self.menu_input_delay_index = 0

    
    def load_level(self):
        pass
    
    def display_button(self, properties, button_color = -1):
        # properties = [text, text_color, font_size, is_bold, pos, size]
        [text_img, text_size] = text2img(properties[0], properties[1], properties[2], properties[3])
        if button_color != -1:
            pygame.draw.rect(self.surface, button_color, [properties[4], properties[5]])
        self.surface.blit(text_img, [properties[4][0]+properties[5][0]/2-text_size[0]/2, properties[4][1]+properties[5][1]/2-text_size[1]/2])
        
    def update(self):
        self.display.blit(pygame.transform.scale(self.surface, self.display_size), [0, 0])
        pygame.display.update()
        self.clock.tick(self.tick)
    
    def close(self):
        pygame.quit()
    

    def handle_menu(self):
        # Select Level
        # Level Editor
        # Players/Controls
        # Quit
        do_menu_navigation = 0
        if self.menu_input_delay_index == 0:
            do_menu_navigation = 1
            self.menu_input_delay_index = 1
            self.menu_input_timestamp = time.time()
        elif self.menu_input_delay_index == 1:
            if self.menu_input_timestamp + self.menu_input_timedelay_first <= time.time():
                do_menu_navigation = 1
                self.menu_input_delay_index = 2
                self.menu_input_timestamp = time.time()
        elif self.menu_input_delay_index == 2:
            if self.menu_input_timestamp + self.menu_input_timedelay_second <= time.time():
                do_menu_navigation = 1
                self.menu_input_timestamp = time.time()
        if do_menu_navigation:
            if self.up:
                self.menu_cursor = (self.menu_cursor - 1) % len(self.menu_buttons)
            if self.down:
                self.menu_cursor = (self.menu_cursor + 1) % len(self.menu_buttons)
        if self.mouse_moved:
            for i in range(0, len(self.menu_buttons)):
                if in_rect(self.mouse_pos, self.menu_buttons[i][4], self.menu_buttons[i][5]):
                    self.menu_cursor = i
        if self.mouse_rmb or self.select:
            if self.menu_cursor == 0:
                # Select Level
                self.page = 'level select'
            elif self.menu_cursor == 1:
                # Level Editor
                self.page = 'level edit select'
            elif self.menu_cursor == 2:
                # Settings
                self.page = 'settings'
            elif self.menu_cursor == 3:
                # Quit
                self.running = 0

    def display_menu(self):
        self.surface.fill(self.menu_color)
        self.display_button(self.menu_title)
        for i in range(0, len(self.menu_buttons)):
            if i == self.menu_cursor:
                self.display_button(self.menu_buttons[i], self.menu_button_color)
            else:
                self.display_button(self.menu_buttons[i])
        
    def handle_level_select(self):
        # Level list w/ preview
        # Press back to return to Menu
        pass
    
    def display_level_select(self):
        pass
    
    def handle_level(self):
        # Load level
        # Play game
        # Once one left win the game
        pass
    
    def display_level(self):
        pass
    
    def handle_win(self):
        # Show winner for a while
        # Then return to the main menu
        pass
    
    def display_win(self):
        pass
    
    def handle_level_edit_select(self):
        # Select level
        # Copy existing level
        # New level
        # Press back to return to Menu
        pass
    
    def display_level_edit_select(self):
        pass
    
    def handle_level_editor_properties(self):
        # Select name
        # Select size
        # Select if player properties are global
        # Select background color
        # Select vertical looping (Add color if deadly boundary)
        # Select horizontal looping (Add wall if not looping)
        pass
    
    def display_level_editor_properties(self):
        pass
    
    def handle_level_editor(self):
        # Add block
            # Set color
            # Set properties
        # Rearrange block hierarchy
        # Move existing blocks
        # Add player
            # Set color
            # Set properties
            # Prevent overlap by shifting player up
        # Move existing players
        # Change existing player properties
        pass
    
    def display_level_editor(self):
        pass
    
    def handle_settings(self):
        # TODO:
        # Work on the settings window next
        # have player profiles that can either be
        # controllers or keyboard maps
        #
        # Make any up control set game.up to 1
        # Same for game.down, and game.select
        #
        # Maybe make arrows, return, space, and
        # tab all default keys in menus regardless
        # of player controls
        
        # Update joysticks
        # Add player
            # Use numeric naming
            # Map controls
            # Pick color
        # Maybe remap option
        # Remove player
        # Return
        pass
    
    def display_settings(self):
        pass
    
class player():
    def __init__(self):
        # name
        # color
        # size
        # alive
        
        # position
        # desired position
        
        # base speed
        # desired speed
        # actual speed
        # acceleration
        # gravity
        # jump strength
        
        # score
        pass

def text2img(text, color, font_size, is_bold):
    font = pygame.font.SysFont('couriernew', font_size, is_bold)
    rendered_text = font.render(text, False, color)
    text_size = font.size(text)
    return rendered_text, text_size

def in_rect(point, rect_pos, rect_size):
    for i in range(0, len(point)):
        if point[i] < rect_pos[i] or point[i] > rect_pos[i] + rect_size[i]:
            return 0
    return 1