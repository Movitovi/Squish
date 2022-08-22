import pygame, os, time, random, math

class game():
    def __init__(self):
        pygame.init()
        self.cwd = os.getcwd()
        self.running = 1
        self.mode = 'page'

        self.load_settings()

        self.sound = sound(self.cwd, self.volume)
        
        pygame.display.set_caption('squish')
        self.surface_icon = pygame.Surface([60, 60])
        self.surface_icon.fill(0xff0000)
        pygame.display.set_icon(self.surface_icon)

        self.restart_display()

        self.clock = pygame.time.Clock()
        self.tick_speed = 50 # NOTE: Change this back to 50
        self.pot_tar = []
        
        self.reset_joysticks()
        self.reset_mapping()
        
        self.load_sprites()
        self.initialize_boosts()

        self.su_rects = []
        self.su_all = 1
        self.su_rect_pad = 6
        self.mode_entrance = 0

        self.page = 'main'
        self.next_page = 'main'
        self.page_pause = 35
        self.page_cnt = 0
        self.mouse_multiplier = [1, 1]
        self.reset_menu_navigation()

        self.reset_editor_tools()

        self.load_levels()

        self.shield_color = 0x010101
        self.max_teams = 4
        self.teaming = 0
        self.team_colors = [0xcc0000, 0x0000cc, 0x00cc00, 0xcc00cc]
        self.winning_team = 0
        self.team_win_text = ['Team 0 Wins!', 'Red Team Wins!', 'Blue Team Wins!', 'Green Team Wins!', 'Purple Team Wins!']
        self.set_cpu_weights()
        self.players_alive = 0
        self.lplayers_alive = 0
        self.load_player_data()

        self.death_animations = []
        self.kill_anis = []

        self.valid_name_inputs = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789'
        self.valid_int_inputs = '0123456789'
        self.valid_float_inputs = '.0123456789'
        self.valid_hex_inputs = '0123456789abcdefABCDEF'
        self.valid_inputs = ''
        self.text_input = ''
        self.text_last_input = ''
        self.text_input_action = -1

        self.kill_width = 0.2
        self.squish_delta = 0.015
        self.winner_index = 0
        self.player_push_constant = 0.5

        self.load_secrets()
        self.secret = ''

        self.ranks = ['1st', '2nd', '3rd', '4th', '5th',
                      '6th', '7th', '8th', '9th', '10th']
        
        self.load_snake_scores()
        self.snake_game = snake_game(self.sound)

        self.load_scythe_scores()
        self.scythe_game = scythe_game(self.cwd, self.sound)

        self.tron_game = tron_game(self.sound)

        self.update_window_size(0)
        
    def restart_display(self, init_display = 1):
        self.display_info = pygame.display.Info()
        self.real_display_size = [self.display_info.current_w, self.display_info.current_h]
        if self.real_display_size[0] == 0:
            self.real_display_size[0] = 1
        if self.real_display_size[1] == 0:
            self.real_display_size[1] = 1
        self.resolutions = [[480, 320], [800, 460], [1280, 720], [1920, 1080]]
        self.display_size = self.resolution
        self.font_multiplier = 0.5 * (self.resolution[0] / 1920 + self.resolution[1] / 1080)
        self.initial_size = self.display_size
        self.screen_scales = [0.9 * self.real_display_size[0] / self.display_size[0], 0.9 * self.real_display_size[1] / self.display_size[1]]
        if init_display:
            self.display = pygame.display.set_mode([self.screen_scales[0] * self.display_size[0], self.screen_scales[1] * self.display_size[1]], pygame.RESIZABLE)
        if self.fullscreen:
            pygame.display.set_mode(self.display_size, pygame.FULLSCREEN)
        self.surface = pygame.Surface(self.display_size)
        self.surface_size = self.surface.get_size()
        if self.surface_size[0] == 0:
            self.surface_size[0] = 1
        if self.surface_size[1] == 0:
            self.surface_size[1] = 1

        self.load_pages()

    def load_sprites(self):
        self.colorkey = 0x010101
        self.sprite_path = os.path.join(self.cwd, 'sprites')
        self.img_boosts = {}
        for file_name in os.listdir(self.sprite_path):
            if file_name[0:5] == 'boost':
                self.img_boosts[file_name.replace('boost_', '').replace('.png', '')] = self.load_sprite(file_name)
        self.img_arrow = self.load_sprite('arrow.png')
        self.img_fire = self.load_sprite('fire.png')
        self.imgs_zap = []
        for i in range(1, 5):
            self.imgs_zap.append(self.load_sprite('zap_' + str(i) + '.png'))

    def load_sprite(self, file_name):
        image = pygame.image.load(os.path.join(self.sprite_path, file_name)).convert()
        image.set_colorkey(self.colorkey)
        return image

    def load_settings(self):
        self.fullscreen = False
        self.required_snake_score = 0
        self.required_scythe_score = 0
        file = open(os.path.join(self.cwd, 'settings.txt'), encoding = 'utf-8')
        for line in file:
            lowercase_line = line.lower()
            no_spaces_line = lowercase_line.replace(' ', '')
            no_comment_line = no_spaces_line.split('#')[0]
            no_return_line = no_comment_line.replace('\n', '')
            split_line = no_return_line.split('=')
            properky = split_line[0]
            value = split_line[-1]
            if properky == 'volume':
                self.volume = int(value)
            elif properky == 'fullscreen':
                self.fullscreen = (value == 'true') or (value == '1')
            elif properky == 'resolution':
                self.resolution = findxy(value, is_int = 1)
                if self.resolution[0] <= 0:
                    self.resolution[0] = 1
                if self.resolution[1] <= 0:
                    self.resolution[1] = 1
            elif properky == 'show_fps':
                self.show_fps = (value == 'true') or (value == '1')
            elif properky == 'boosts_on':
                self.boosts_on = (value == 'true') or (value == '1')
            elif properky == 'boost_periodicity':
                self.boost_periodicity = int(value)
            elif properky == 'boost_draw_pile':
                self.boost_draw_pile = int(value)
            elif properky == 'team_count':
                self.team_count = int(value)
            elif properky == 'required_snake_score':
                self.required_snake_score = int(value)
            elif properky == 'required_scythe_score':
                self.required_scythe_score = int(value)
        file.close()

    def save_settings(self):
        file = open(os.path.join(self.cwd, 'settings.txt'), mode = 'w', encoding = 'utf-8')
        file.write('volume = ' + str(self.volume) + '\n')
        file.write('fullscreen = ' + 'true' * (self.fullscreen) + 'false' * (not self.fullscreen) + '\n')
        file.write('resolution = ' + str(self.resolution) + '\n')
        file.write('show_fps = ' + 'true' * (self.show_fps) + 'false' * (not self.show_fps) + '\n')
        file.write('boosts_on = ' + 'true' * (self.boosts_on) + 'false' * (not self.boosts_on) + '\n')
        file.write('boost_periodicity = ' + str(self.boost_periodicity) + '\n')
        file.write('boost_draw_pile = ' + str(self.boost_draw_pile) + '\n')
        file.write('team_count = ' + str(self.team_count) + '\n')
        file.write('required_snake_score = ' + str(self.required_snake_score) + '\n')
        file.write('required_scythe_score = ' + str(self.required_scythe_score))
        file.close()

    def reset_menu_navigation(self):
        self.cursor = [0, 0]
        self.last_cursor = [0, 0]
        self.cursor_on_list = 0
        self.mouse_lmb = 1
        self.mouse_last_lmb = 1
        self.mouse_rmb = 1
        self.mouse_last_rmb = 1
        self.mouse_wheel = 0
        self.scroll_speed = 65
        self.menu_controls = {'up': 0,
                              'down': 0,
                              'left': 0,
                              'right': 0,
                              'select': 0,
                              'back': 0,
                              'page_entrance': 0,
                              'continual': 1}
        self.menu_input_delay_index = [0, 0]
        self.menu_input_timedelay_first = 0.5
        self.menu_input_timedelay_second = 0.1
        self.menu_input_timestamp = [time.time() - self.menu_input_timedelay_first, time.time() - self.menu_input_timedelay_first]
        self.slider_latch = 0
        pygame.mouse.set_visible(1)

    def reset_joysticks(self):
        self.joystick_threshold = 0.5
        self.joysticks = []
        self.controllers = []
        for i in range(0, pygame.joystick.get_count()):
            self.joysticks.append(pygame.joystick.Joystick(i))
            self.joysticks[i].init()
            self.controllers.append(controller(self.joysticks[i], self.joystick_threshold))

    def reset_mapping(self):
        self.mapping = 0
        self.current_map = ''
        self.has_mapped = 1
        self.do_joy = 0
        self.do_hat = 0
        self.new_controls = {}
    
    def map_controls(self):
        if not self.mapping:
            self.new_controls = self.players[-1].controls
            self.mapping = 1
        if self.has_mapped:
            this_control = 0
            if self.current_map == '':
                self.new_controls
                this_control = 1
            for control in self.players[-1].controls:
                if this_control:
                    self.current_map = control
                    self.has_mapped = 0
                    break
                if self.current_map == control:
                    this_control = 1
            if self.has_mapped:
                self.players[-1].controls = self.new_controls
                self.reset_mapping()
                self.do_actions([['goto', 'add_player']])
        
    def map_event(self):
        no_joy = 1
        no_hat = 1
        for joy in self.joysticks:
            for axis in range(0, joy.get_numaxes() - 2):
                if abs(joy.get_axis(axis)) >= self.joystick_threshold:
                    no_joy = 0
            for axis in range(joy.get_numaxes() - 2, joy.get_numaxes()):
                if joy.get_axis(axis) >= self.joystick_threshold:
                    no_joy = 0
            for hat in range(0, joy.get_numhats()):
                if joy.get_hat(hat) != (0, 0):
                    no_hat = 0
        if no_joy:
            self.do_joy = 1
        if no_hat:
            self.do_hat = 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.menu_controls['select'] = 1
                else:
                    self.new_controls[self.current_map] = [-1, event.key, 0, 0]
                    self.has_mapped = 1
                    break
            elif event.type == pygame.JOYBUTTONDOWN:
                self.new_controls[self.current_map] = [event.joy, 'button', event.button, 1, 0, 0]
                self.has_mapped = 1
                break
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis >= 4:
                    if event.value < 0:
                        value = 0
                    else:
                        value = event.value
                else:
                    value = event.value
                if self.do_joy and (abs(value) >= self.joystick_threshold):
                    if value >= 0:
                        direction = 1
                    else:
                        direction = -1
                    self.new_controls[self.current_map] = [event.joy, 'axis', event.axis, direction, 0, 0]
                    self.has_mapped = 1
                    self.do_joy = 0
                    break
            elif event.type == pygame.JOYHATMOTION:
                if self.do_hat and ((event.value[0] != 0) ^ (event.value[1] != 0)):
                    self.new_controls[self.current_map] = [event.joy, 'hat', event.hat, event.value[:], 0, 0]
                    self.has_mapped = 1
                    self.do_hat = 0
                    break
            elif (event.type == pygame.JOYDEVICEADDED) or (event.type == pygame.JOYDEVICEREMOVED):
                self.reset_joysticks()
            elif event.type == pygame.WINDOWRESIZED:
                self.update_window_size()

    def find_list_buttons(self):
        self.pages[self.page].button_array = [[0]]
        for button in self.pages[self.page].buttons:
            for i in range(len(self.pages[self.page].button_array), max(button.button_pos) + 1):
                self.pages[self.page].button_array.append([0])
                for ii in range(0, len(self.pages[self.page].button_array[0])):
                    self.pages[self.page].button_array[ii].append(0)
                    self.pages[self.page].button_array[-1].append(0)
            self.pages[self.page].button_array[button.button_pos[0]][button.button_pos[1]] = 1
        for lisk in self.pages[self.page].lists:
            if lisk.selectable:
                list_length = len(self.players) * (lisk.type == 'player') + len(self.levels) * (lisk.type == 'level')
                for i in range(len(self.pages[self.page].button_array), max([lisk.select_pos[0], lisk.select_pos[1] + list_length - 1]) + 1):
                    self.pages[self.page].button_array.append([0])
                    for ii in range(0, len(self.pages[self.page].button_array[0])):
                        self.pages[self.page].button_array[ii].append(0)
                        self.pages[self.page].button_array[-1].append(0)
                for i in range(0, list_length):
                    self.pages[self.page].button_array[lisk.select_pos[0]][lisk.select_pos[1] + i] = 1
        for slider in self.pages[self.page].sliders:
            for i in range(len(self.pages[self.page].button_array), max(slider.button_pos) + 1):
                self.pages[self.page].button_array.append([0])
                for ii in range(0, len(self.pages[self.page].button_array[0])):
                    self.pages[self.page].button_array[ii].append(0)
                    self.pages[self.page].button_array[-1].append(0)
            self.pages[self.page].button_array[slider.button_pos[0]][slider.button_pos[1]] = 1
    
    def draw_alpha(self, color, alpha):
        alpha_surface = pygame.Surface(self.display_size)
        alpha_surface.fill(color)
        alpha_surface.set_alpha(alpha)
        self.surface.blit(alpha_surface, [0, 0])

    def get_page_inputs(self):
        self.mouse_moved = not ((0, 0) == pygame.mouse.get_rel())
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pos = [self.mouse_pos[0] * self.mouse_multiplier[0], self.mouse_pos[1] * self.mouse_multiplier[1]]
        self.mouse_last_lmb = self.mouse_lmb
        self.mouse_lmb = pygame.mouse.get_pressed()[0]
        self.mouse_wheel = 0
        if not self.mapping:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = 0
                elif event.type == pygame.MOUSEWHEEL:
                    self.mouse_wheel = event.y * self.scroll_speed
                elif (event.type == pygame.KEYDOWN) or (event.type == pygame.KEYUP):
                    key_direction = (event.type == pygame.KEYDOWN)
                    if (event.key == pygame.K_UP) or (event.key == pygame.K_w):
                        if not self.teaming or not self.check_player_team_event(event):
                            self.menu_controls['up'] = key_direction
                            self.menu_input_delay_index[1] = 0
                    elif (event.key == pygame.K_DOWN) or (event.key == pygame.K_s):
                        if not self.teaming or not self.check_player_team_event(event):
                            self.menu_controls['down'] = key_direction
                            self.menu_input_delay_index[1] = 0
                    elif (event.key == pygame.K_LEFT) or (event.key == pygame.K_a):
                        if not self.teaming or not self.check_player_team_event(event):
                            self.menu_controls['left'] = key_direction
                            self.menu_input_delay_index[0] = 0
                    elif (event.key == pygame.K_RIGHT) or (event.key == pygame.K_d):
                        if not self.teaming or not self.check_player_team_event(event):
                            self.menu_controls['right'] = key_direction
                            self.menu_input_delay_index[0] = 0
                    elif event.key == pygame.K_RETURN:
                        self.menu_controls['select'] = key_direction
                    elif event.key == pygame.K_ESCAPE:
                        self.menu_controls['back'] = key_direction
                    if key_direction and (self.text_input_action != -1):
                        if event.key == pygame.K_BACKSPACE:
                            self.text_input = self.text_input[:-1]
                        elif (self.text_input_limit == -1) or (len(self.text_input) < self.text_input_limit):
                            if self.valid_inputs.count(event.unicode):
                                if self.valid_inputs == self.valid_float_inputs:
                                    if self.text_input.count('.') >= 1:
                                        if event.unicode == '.':
                                            continue
                                        elif len(self.text_input) - self.text_input.find('.') >= 5:
                                            continue
                                self.text_input += event.unicode
                        self.apply_text_input(self.text_input)
                elif (event.type == pygame.JOYDEVICEADDED) or (event.type == pygame.JOYDEVICEREMOVED):
                    self.reset_joysticks()
                elif (event.type == pygame.WINDOWRESIZED) or (event.type == pygame.WINDOWMOVED) or (event.type == pygame.WINDOWEXPOSED):
                    self.update_window_size()

            for i in range(0, len(self.controllers)):
                kontroller = self.controllers[i]
                kontroller.check_inputs(self, si = i)
                
        else:
            self.map_event()

    def load_pages(self):
        pgd = os.path.join(self.cwd, 'pages')
        self.pages = {}
        for pg in os.listdir(pgd):
            file = open(os.path.join(pgd, pg), encoding = 'utf-8')
            self.pages[pg.replace('.txt', '')] = page(file.readlines(), self.display_size, self)
            file.close()

    def run_page(self):
        if self.mode_entrance:
            self.mode_entrance = 0
            self.su_all = 1
        
        if self.menu_controls['page_entrance']:
            if self.pages[self.page].settings.count('take_screenshot'):
                self.surface_screenshot = self.surface.copy()
            else:
                self.surface_screenshot = None
            if self.pages[self.page].settings.count('page_pause'):
                self.page_cnt = self.page_pause
            else:
                self.page_cnt = 0
            self.reset_menu_navigation()
            self.find_list_buttons()
            for i in range(0, len(self.pages[self.page].lists)):
                self.pages[self.page].lists[i].scroll_value = 0
            for control in self.pages[self.page].controls:
                if control.trigger == 'page_entrance':
                    self.do_actions(control.actions)
        
        if self.page_cnt > 0:
            self.reset_menu_navigation()
            self.mouse_moved = 0
            self.page_cnt -= 1

        if self.surface_screenshot:
            self.surface.blit(pygame.transform.scale(self.surface_screenshot, self.surface_size), [0, 0])

        for control in self.pages[self.page].controls:
            if control.trigger == 'continual_early':
                self.do_actions(control.actions)

        self.last_cursor = [self.cursor[0], self.cursor[1]]

        self.get_player_inputs()
        for block in self.pages[self.page].blocks:
            if block.dynamic_color:
                if block.dynamic_color[0] == 'level':
                    if block.dynamic_color[1] == 'background_color':
                        block.color = self.levels[self.level].background_color
                if block.dynamic_color[0] == 'game':
                    if block.dynamic_color[1] == 'team_count':
                        block.color = block.color_main
                        if block.dynamic_color[2] == '3':
                            if self.team_count < 3:
                                block.color = block.color_alt
                        elif block.dynamic_color[2] == '4':
                            if self.team_count < 4:
                                block.color = block.color_alt
                elif block.dynamic_color[0] == 'editor':
                    if block.dynamic_color[1] == 'block_color':
                        block.color = self.editor_block_color
                    elif block.dynamic_color[1] == 'block':
                        if block.dynamic_color[2] == 'color':
                            block.color = self.edited_block.color
                    elif block.dynamic_color[1] == 'background':
                        if block.dynamic_color[2] == 'color':
                            block.color = self.edited_background
            if block.text_variable != '':
                variable_text = ''
                if block.text_variable == 'controller_count':
                    variable_text = block.text.format(str(len(self.controllers))[0:block.text_variable_char_limit])
                elif block.text_variable == 'present_map':
                    if self.current_map == '':
                        variable_text = block.text.format('left'.capitalize()[0:block.text_variable_char_limit])
                    else:
                        variable_text = block.text.format(self.current_map.capitalize()[0:block.text_variable_char_limit])
                elif block.text_variable == 'winner':
                    if self.team_count <= 0:
                        if self.winner_index != None:
                            if self.winner_index < len(self.players):
                                winner_name = self.players[self.winner_index].name
                                if len(winner_name) > 0:
                                    if winner_name[0].isupper():
                                        variable_text = block.text.format(winner_name[0:block.text_variable_char_limit] + ' W')
                                    else:
                                        variable_text = block.text.format(winner_name[0:block.text_variable_char_limit] + ' w')
                        else:
                            variable_text = 'Nobody Wins!'
                    else:
                        variable_text = self.team_win_text[self.winning_team]
                elif block.text_variable == 'snake_score':
                    variable_text = block.text.format(self.snake_game.score)
                elif block.text_variable == 'scythe_score':
                    variable_text = block.text.format(round(self.scythe_game.score))
                if len(self.players):
                    plajer = self.players[-1]
                    for control in plajer.controls:
                        if block.text_variable == 'control_' + control:
                            if plajer.controls[control][-1]:
                                variable_text = control.capitalize()
                [block.text_image, new_text_image_size] = self.text2img(variable_text, block.text_color, block.text_font, block.text_size, block.text_bold)
                self.su_rects.append([block.pos, block.size])
            if block.color != -1:
                block_surface = pygame.Surface(block.size)
                block_surface.fill(block.color)
                if block.alpha != 255:
                    block_surface.set_alpha(block.alpha)
                    self.su_rects.append([block.pos, block.size])
                self.surface.blit(block_surface, block.pos)
            if block.text_image != 0:
                if block.text_dynamic_pos:
                    block.text_pos = findxy(block.text_pos_string, block.size, block.pos, new_text_image_size)
                self.surface.blit(block.text_image, block.text_pos)
        
        active_things = []
        ocursor = self.cursor[:]
        
        do_menu_navigation = [0, 0]
        if self.text_input_action == -1:
            for i in range(0, 2):
                if self.menu_input_delay_index[i] == 0:
                    do_menu_navigation[i] = 1
                    self.menu_input_delay_index[i] = 1
                    self.menu_input_timestamp[i] = time.time()
                elif self.menu_input_delay_index[i] == 1:
                    if self.menu_input_timestamp[i] + self.menu_input_timedelay_first <= time.time():
                        do_menu_navigation[i] = 1
                        self.menu_input_delay_index[i] = 2
                        self.menu_input_timestamp[i] = time.time()
                elif self.menu_input_delay_index[i] == 2:
                    if self.menu_input_timestamp[i] + self.menu_input_timedelay_second <= time.time():
                        do_menu_navigation[i] = 1
                        self.menu_input_timestamp[i] = time.time()
            
            for button in self.pages[self.page].buttons:
                if in_rect(self.mouse_pos, button.pos, button.size) and not self.slider_latch:
                    if self.mouse_moved:
                        do_menu_navigation = [0, 0]
                        self.cursor = [button.button_pos[0], button.button_pos[1]]
                    if self.mouse_lmb and not self.mouse_last_lmb:
                        do_menu_navigation = [0, 0]
                        self.cursor = [button.button_pos[0], button.button_pos[1]]
                        self.menu_controls['select'] = 1
            
            for lisk in self.pages[self.page].lists:
                if lisk.selectable:
                    if in_rect(self.mouse_pos, lisk.pos, lisk.size) and not self.slider_latch:
                        list_length = len(self.players) * ((lisk.type == 'player') or (lisk.type == 'score')) + len(self.levels) * (lisk.type == 'level') + len(self.snake_scores) * (lisk.type == 'snake_score') + len(self.scythe_scores) * (lisk.type == 'scythe_score')
                        for i in range(0, list_length):
                            entry_pos = [lisk.pos[0], lisk.pos[1] + i * (lisk.entry_size[1] + lisk.entry_spacing) + lisk.scroll_value]
                            if in_rect(self.mouse_pos, entry_pos, lisk.entry_size):
                                if self.mouse_moved:
                                    do_menu_navigation = [0, 0]
                                    self.cursor = [lisk.select_pos[0], lisk.select_pos[1] + i]
                                    self.cursor_on_list = 1
                                if self.mouse_lmb and not self.mouse_last_lmb:
                                    do_menu_navigation = [0, 0]
                                    self.cursor = [lisk.select_pos[0], lisk.select_pos[1] + i]
                                    self.cursor_on_list = 1
                                    self.menu_controls['select'] = 1
            
            for slider in self.pages[self.page].sliders:
                if in_rect(self.mouse_pos, slider.pos, slider.size) and not self.slider_latch:
                    if self.mouse_moved:
                        do_menu_navigation = [0, 0]
                        self.cursor = [slider.button_pos[0], slider.button_pos[1]]
                    if self.mouse_lmb and not self.mouse_last_lmb:
                        do_menu_navigation = [0, 0]
                        self.cursor = [slider.button_pos[0], slider.button_pos[1]]

            dont_direct_horizontal_cursor = 0
            dont_direct_vertical_cursor = 0
            for setting in self.pages[self.page].settings:
                if setting == 'dont_direct_horizontal_cursor':
                    dont_direct_horizontal_cursor = 1
                elif setting == 'dont_direct_vertical_cursor':
                    dont_direct_vertical_cursor = 1
            if do_menu_navigation[1]:
                if self.menu_controls['up']:
                    for i in range(0, len(self.pages[self.page].button_array)**2):
                        self.cursor[1] = (self.cursor[1] - 1) % len(self.pages[self.page].button_array)
                        if self.pages[self.page].button_array[self.cursor[0]][self.cursor[1]] != 1:
                            if self.cursor_on_list or dont_direct_vertical_cursor:
                                continue
                            for ii in range(0, len(self.pages[self.page].button_array)):
                                if self.pages[self.page].button_array[ii][self.cursor[1]] == 1:
                                    self.cursor[0] = ii
                                    break
                            else:
                                continue
                            break
                        else:
                            break
                if self.menu_controls['down']:
                    for i in range(0, len(self.pages[self.page].button_array)**2):
                        self.cursor[1] = (self.cursor[1] + 1) % len(self.pages[self.page].button_array)
                        if self.pages[self.page].button_array[self.cursor[0]][self.cursor[1]] != 1:
                            if self.cursor_on_list or dont_direct_vertical_cursor:
                                continue
                            for ii in range(0, len(self.pages[self.page].button_array)):
                                if self.pages[self.page].button_array[ii][self.cursor[1]] == 1:
                                    self.cursor[0] = ii
                                    break
                            else:
                                continue
                            break
                        else:
                            break
            if do_menu_navigation[0]:
                if self.menu_controls['left']:
                    for i in range(0, len(self.pages[self.page].button_array) ** 2):
                        self.cursor[0] = (self.cursor[0] - 1) % len(self.pages[self.page].button_array)
                        if self.pages[self.page].button_array[self.cursor[0]][self.cursor[1]] != 1:
                            if dont_direct_horizontal_cursor:
                                continue
                            for ii in range(0, len(self.pages[self.page].button_array)):
                                if self.pages[self.page].button_array[self.cursor[0]][ii] == 1:
                                    self.cursor[1] = ii
                                    break
                            else:
                                continue
                            break
                        else:
                            break
                if self.menu_controls['right']:
                    for i in range(0, len(self.pages[self.page].button_array)**2):
                        self.cursor[0] = (self.cursor[0] + 1) % len(self.pages[self.page].button_array)
                        if self.pages[self.page].button_array[self.cursor[0]][self.cursor[1]] != 1:
                            if dont_direct_horizontal_cursor:
                                continue
                            for ii in range(0, len(self.pages[self.page].button_array)):
                                if self.pages[self.page].button_array[self.cursor[0]][ii] == 1:
                                    self.cursor[1] = ii
                                    break
                            else:
                                continue
                            break
                        else:
                            break
        else:
            if self.menu_controls['select'] or (self.mouse_lmb and not self.mouse_last_lmb):
                self.menu_controls['select'] = 0
                self.text_input_action = -1
                pygame.key.set_repeat()
            elif self.menu_controls['back']:
                self.apply_text_input(self.text_last_input)
                self.text_input_action = -1
                self.menu_controls['back'] = 0
                pygame.key.set_repeat()
        
        self.cursor_on_list = 0
        for lisk in self.pages[self.page].lists:
            if lisk.team == None:
                list_length = len(self.players) * ((lisk.type == 'player') or (lisk.type == 'score')) + len(self.levels) * (lisk.type == 'level') + len(self.snake_scores) * (lisk.type == 'snake_score') + len(self.scythe_scores) * (lisk.type == 'scythe_score')
            else:
                if lisk.team > self.team_count:
                    continue
                list_players = []
                for plajer in self.players:
                    if plajer.team == lisk.team:
                        list_players.append(plajer)
                list_length = len(list_players)
                self.su_rects.append([lisk.pos, lisk.size])
            if self.mouse_wheel and not lisk.only_last:
                lisk.scroll(self.mouse_wheel, list_length)
                self.su_rects.append([lisk.pos, lisk.size])
            if lisk.selectable:
                if self.cursor[0] == lisk.select_pos[0]:
                    if self.cursor[1] >= lisk.select_pos[1]:
                        if self.cursor[1] < lisk.select_pos[1] + list_length:
                            self.cursor_on_list = 1
                            if self.cursor != self.last_cursor:
                                selected_corner = (self.cursor[1] - lisk.select_pos[1]) * (lisk.entry_size[1] + lisk.entry_spacing) + lisk.scroll_value
                                if selected_corner + lisk.entry_size[1] > lisk.size[1]:
                                    lisk.scroll(-1 * (selected_corner - lisk.size[1] + lisk.entry_size[1]), list_length)
                                    self.su_rects.append([lisk.pos, lisk.size])
                                elif selected_corner < 0:
                                    lisk.scroll(-1 * selected_corner, list_length)
                                    self.su_rects.append([lisk.pos, lisk.size])
                            if self.menu_controls['select']:
                                self.menu_controls['select'] = 0
                                self.do_actions(lisk.actions, self.cursor[1] - lisk.select_pos[1])
                                self.su_rects.append([lisk.pos, lisk.size])
            list_surface = pygame.Surface(lisk.size)
            list_surface.fill(lisk.color)
            if lisk.team == None:
                list_length = len(self.players) * ((lisk.type == 'player') or (lisk.type == 'score')) + len(self.levels) * (lisk.type == 'level') + len(self.snake_scores) * (lisk.type == 'snake_score') + len(self.scythe_scores) * (lisk.type == 'scythe_score')
            for i in range((lisk.only_last) * (list_length - 1), list_length):
                entry_surface = pygame.Surface(lisk.entry_size)
                entry_surface.fill(lisk.entry_color)
                entry_name = ''
                if lisk.selectable:
                    if self.cursor == [lisk.select_pos[0], lisk.select_pos[1] + i]:
                        entry_surface.fill(lisk.select_color)
                if (lisk.type == 'player') or (lisk.type == 'score'):
                    if lisk.team == None:
                        entry = self.players[i]
                    else:
                        entry = list_players[i]
                    entry_name = entry.name
                    pygame.draw.rect(entry_surface, entry.base_color, [lisk.image_pos, lisk.image_size])
                    if lisk.type == 'score':
                        score_image = self.text2img(str(entry.wins), lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)
                        score_image_pos = [lisk.wins_pos[0] - score_image[1][0] / 2, lisk.wins_pos[1]]
                        entry_surface.blit(score_image[0], score_image_pos)
                        score_image = self.text2img(str(entry.kills), lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)
                        score_image_pos = [lisk.kills_pos[0] - score_image[1][0] / 2, lisk.kills_pos[1]]
                        entry_surface.blit(score_image[0], score_image_pos)
                    elif lisk.only_last:
                        self.su_rects.append([lisk.pos, lisk.size])
                elif lisk.type == 'level':
                    entry = self.levels[[*self.levels][i]]
                    entry_name = entry.name
                    pygame.draw.rect(entry_surface, lisk.frame_color, [lisk.frame_pos, lisk.frame_size])
                    entry_surface.blit(pygame.transform.scale(entry.thumbnail, lisk.image_size), lisk.image_pos)
                elif lisk.type == 'snake_score':
                    entry = self.snake_scores[i]
                    entry_name = entry[1]
                    rank_image = self.text2img(self.ranks[i], lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)
                    rank_image_pos = [lisk.rank_pos[0] - rank_image[1][0] / 2, lisk.rank_pos[1]]
                    entry_surface.blit(rank_image[0], rank_image_pos)
                    pygame.draw.rect(entry_surface, entry[2], [lisk.image_pos, lisk.image_size])
                    score_image = self.text2img(str(entry[0]).rjust(5), lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)
                    score_image_pos = [lisk.score_pos[0] - score_image[1][0] / 2, lisk.score_pos[1]]
                    entry_surface.blit(score_image[0], score_image_pos)
                elif lisk.type == 'scythe_score':
                    entry = self.scythe_scores[i]
                    rank_image = self.text2img(self.ranks[i], lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)
                    rank_image_pos = [lisk.rank_pos[0] - rank_image[1][0] / 2, lisk.rank_pos[1]]
                    entry_surface.blit(rank_image[0], rank_image_pos)
                    score_image = self.text2img(str(entry).rjust(7), lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)
                    score_image_pos = [lisk.score_pos[0] - score_image[1][0] / 2, lisk.score_pos[1]]
                    entry_surface.blit(score_image[0], score_image_pos)
                if lisk.only_last:
                    i = 0
                if entry_name != '':
                    if lisk.text_limit == None:
                        entry_surface.blit(self.text2img(entry_name, lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)[0], lisk.text_pos)
                    else:
                        text_surface = pygame.Surface(lisk.text_limit, pygame.SRCALPHA)
                        text_surface.blit(self.text2img(entry_name, lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)[0], [0, 0])
                        entry_surface.blit(text_surface, lisk.text_pos)
                list_surface.blit(entry_surface, [0, i * (lisk.entry_size[1] + lisk.entry_spacing) + lisk.scroll_value])
            self.surface.blit(list_surface, lisk.pos)

        for button in self.pages[self.page].buttons:
            if button.dynamic_color:
                if button.dynamic_color[0] == 'level':
                    if button.dynamic_color[1] == 'background_color':
                        button.color = self.levels[self.level].background_color
                        button.active_color = self.levels[self.level].background_color
                elif button.dynamic_color[0] == 'editor':
                    if button.dynamic_color[1] == 'block_color':
                        button.color = self.editor_block_color
                        button.active_color = self.editor_block_color
                    elif button.dynamic_color[1] == 'block':
                        if button.dynamic_color[2] == 'color':
                            button.color = self.edited_block.color
                            button.active_color = self.edited_block.color
                    elif button.dynamic_color[1] == 'background':
                        if button.dynamic_color[2] == 'color':
                            button.color = self.edited_background
                            button.active_color = self.edited_background
                self.su_rects.append([button.pos, button.size])

            if self.cursor == button.button_pos:
                if self.menu_controls['select']:
                    self.menu_controls['select'] = 0
                    self.do_actions(button.actions)
                had_action = 0
                for action in button.actions:
                    if self.text_input_action == action:
                        had_action = 1
                        break
                if had_action:
                    pygame.draw.rect(self.surface, button.text_active_color, [button.pos, button.size])
                    self.su_rects.append([button.pos, button.size])
                else:
                    pygame.draw.rect(self.surface, button.active_color, [button.pos, button.size])
            elif button.color != -1:
                pygame.draw.rect(self.surface, button.color, [button.pos, button.size])
            if button.text_image != 0:
                button_text = button.text
                had_input = 0
                for action in button.actions:
                    if action[0] == 'input':
                        # HERE 3
                        if action[1] == 'level':
                            if action[2] == 'name':
                                button.text_input = self.levels[self.level].name
                            elif action[2] == 'width':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                else:
                                    button.text_input = str(self.levels[self.level].size[0])
                            elif action[2] == 'height':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                else:
                                    button.text_input = str(self.levels[self.level].size[1])
                            elif action[2] == 'background_color':
                                if self.text_input_action == action:
                                    button.text_input = '0x' + self.text_input
                                else:
                                    button.text_input = '{0:#0{1}x}'.format(self.levels[self.level].background_color, 8)
                            elif action[2] == 'side_wall_depth':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                elif self.levels[self.level].side_wall_depth == 0:
                                    button.text_input = '0.0'
                                else:
                                    button.text_input = str(self.levels[self.level].side_wall_depth)
                        elif action[1] == 'player':
                            if action[2] == 'name':
                                button.text_input = self.players[-1].name
                            elif action[2] == 'base_color':
                                if self.text_input_action == action:
                                    button.text_input = '0x' + self.text_input
                                else:
                                    button.text_input = '{0:#0{1}x}'.format(self.players[-1].base_color, 8)
                            elif action[2] == 'width':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                elif self.levels[self.level].player_size[0] == 0:
                                    button.text_input = '0.0'
                                else:
                                    button.text_input = str(self.levels[self.level].player_size[0])
                            elif action[2] == 'height':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                elif self.levels[self.level].player_size[1] == 0:
                                    button.text_input = '0.0'
                                else:
                                    button.text_input = str(self.levels[self.level].player_size[1])
                            elif action[2] == 'gravity':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                elif self.levels[self.level].player_gravity == 0:
                                    button.text_input = '0.0'
                                else:
                                    button.text_input = str(self.levels[self.level].player_gravity)
                            elif action[2] == 'jump_strength':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                elif self.levels[self.level].player_jump_strength == 0:
                                    button.text_input = '0.0'
                                else:
                                    button.text_input = str(self.levels[self.level].player_jump_strength)
                            elif action[2] == 'y_vel_terminal':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                elif self.levels[self.level].player_vel_terminal[1] == 0:
                                    button.text_input = '0.0'
                                else:
                                    button.text_input = str(self.levels[self.level].player_vel_terminal[1])
                            elif action[2] == 'x_vel_terminal':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                elif self.levels[self.level].player_vel_terminal[0] == 0:
                                    button.text_input = '0.0'
                                else:
                                    button.text_input = str(self.levels[self.level].player_vel_terminal[0])
                            elif action[2] == 'y_vel_delta':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                elif self.levels[self.level].player_vel_delta[1] == 0:
                                    button.text_input = '0.0'
                                else:
                                    button.text_input = str(self.levels[self.level].player_vel_delta[1])
                            elif action[2] == 'x_vel_delta':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                elif self.levels[self.level].player_vel_delta[0] == 0:
                                    button.text_input = '0.0'
                                else:
                                    button.text_input = str(self.levels[self.level].player_vel_delta[0])
                            elif action[2] == 'shield_health':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                elif self.levels[self.level].player_shield_health_base == 0:
                                    button.text_input = '0.0'
                                else:
                                    button.text_input = str(self.levels[self.level].player_shield_health_base)
                            elif action[2] == 'shield_regen':
                                if self.text_input_action == action:
                                    button.text_input = self.text_input
                                elif self.levels[self.level].player_shield_regen == 0:
                                    button.text_input = '0.0'
                                else:
                                    button.text_input = str(self.levels[self.level].player_shield_regen)
                        elif action[1] == 'editor':
                            if action[2] == 'block_color':
                                if self.text_input_action == action:
                                    button.text_input = '0x' + self.text_input
                                else:
                                    button.text_input = '{0:#0{1}x}'.format(self.editor_block_color, 8)
                            elif action[2] == 'block':
                                if action[3] == 'color':
                                    if self.text_input_action == action:
                                        button.text_input = '0x' + self.text_input
                                    else:
                                        button.text_input = '{0:#0{1}x}'.format(self.edited_block.color, 8)
                                elif action[3] == 'x_pos':
                                    if self.text_input_action == action:
                                        button.text_input = self.text_input
                                    elif self.edited_block.pos[0] == 0:
                                        button.text_input = '0'
                                    else:
                                        button.text_input = str(self.edited_block.pos[0])
                                elif action[3] == 'y_pos':
                                    if self.text_input_action == action:
                                        button.text_input = self.text_input
                                    elif self.edited_block.pos[1] == 0:
                                        button.text_input = '0'
                                    else:
                                        button.text_input = str(self.edited_block.pos[1])
                                elif action[3] == 'x_size':
                                    if self.text_input_action == action:
                                        button.text_input = self.text_input
                                    elif self.edited_block.size[0] == 0:
                                        button.text_input = '0'
                                    else:
                                        button.text_input = str(self.edited_block.size[0])
                                elif action[3] == 'y_size':
                                    if self.text_input_action == action:
                                        button.text_input = self.text_input
                                    elif self.edited_block.size[1] == 0:
                                        button.text_input = '0'
                                    else:
                                        button.text_input = str(self.edited_block.size[1])
                            elif action[2] == 'player':
                                if action[3] == 'x_pos':
                                    if self.text_input_action == action:
                                        button.text_input = self.text_input
                                    elif self.edited_player_pos[0] == 0:
                                        button.text_input = '0'
                                    else:
                                        button.text_input = str(self.edited_player_pos[0])
                                elif action[3] == 'y_pos':
                                    if self.text_input_action == action:
                                        button.text_input = self.text_input
                                    elif self.edited_player_pos[1] == 0:
                                        button.text_input = '0'
                                    else:
                                        button.text_input = str(self.edited_player_pos[1])
                            elif action[2] == 'background':
                                if action[3] == 'color':
                                    if self.text_input_action == action:
                                        button.text_input = '0x' + self.text_input
                                    else:
                                        button.text_input = '{0:#0{1}x}'.format(self.edited_background, 8)
                        had_input = 1
                    elif action[0] == 'toggle':
                        if action[1] == 'level':
                            if action[2] == 'vertical_looping':
                                button.text_input = str(self.levels[self.level].vertical_looping)
                            elif action[2] == 'horizontal_looping':
                                button.text_input = str(self.levels[self.level].horizontal_looping)
                        elif action[1] == 'player':
                            if action[2] == 'is_cpu':
                                button.text_input = str(self.players[-1].is_cpu)
                        elif action[1] == 'game':
                            if action[2] == 'show_fps':
                                button.text_input = str(self.show_fps)
                            elif action[2] == 'resolution':
                                button.text_input = str(self.resolution[0]) + 'x' + str(self.resolution[1])
                            elif action[2] == 'boosts_on':
                                button.text_input = str(self.boosts_on)
                            elif action[2] == 'team_count':
                                button.text_input = str(self.team_count)
                        elif action[1] == 'editor':
                            if action[2] == 'mirroring':
                                button.text_input = str(self.editor_mirroring)
                            elif action[2] == 'block_solid':
                                button.text_input = str(self.editor_block_solid)
                            elif action[2] == 'block':
                                if action[3] == 'solid':
                                    button.text_input = str(self.edited_block.solid)
                        had_input = 1
                input_surface = pygame.Surface(button.text_window_size, pygame.SRCALPHA)
                if had_input:
                    input_surface.blit(self.text2img(button_text + button.text_input, button.text_color, button.text_font, button.text_size, button.text_bold)[0], [0, 0])
                    self.su_rects.append([button.pos, button.size])
                else:
                    input_surface.blit(button.text_image, [0, 0])
                self.surface.blit(input_surface, button.text_pos)

        for slider in self.pages[self.page].sliders:
            if self.cursor == slider.button_pos:
                addition = 0
                if self.menu_controls['left']:
                    addition += -1
                if self.menu_controls['right']:
                    addition += 1
                addition += round(0.1 * self.mouse_wheel)
                if self.mouse_lmb:
                    if in_rect(self.mouse_pos, slider.slider_pos, slider.slider_size) or self.slider_latch:
                        self.su_rects.append([slider.pos, slider.size])
                        self.slider_latch = 1
                        if slider.slider_size[0] != 0:
                            slider.percent = (self.mouse_pos[0] - slider.slider_pos[0]) / slider.slider_size[0]
                            value = round(slider.min_value + slider.percent * (slider.max_value - slider.min_value))
                            for action in slider.actions:
                                if action[0] == 'set':
                                    if action[1] == 'volume':
                                        self.volume = keep_within(value, slider.min_value, slider.max_value)
                                        self.sound.set_volume(self.volume)
                                    elif action[1] == 'boost_periodicity':
                                        self.boost_periodicity = keep_within(value, slider.min_value, slider.max_value)
                                    elif action[1] == 'boost_draw_pile':
                                        self.boost_draw_pile = keep_within(value, slider.min_value, slider.max_value)
                else:
                    self.slider_latch = 0
                if addition:
                    self.su_rects.append([slider.pos, slider.size])
                    for action in slider.actions:
                        if action[0] == 'set':
                            if action[1] == 'volume':
                                self.volume = keep_within(self.volume + addition, slider.min_value, slider.max_value)
                                self.sound.set_volume(self.volume)
                            elif action[1] == 'boost_periodicity':
                                self.boost_periodicity = keep_within(self.boost_periodicity + addition, slider.min_value, slider.max_value)
                            elif action[1] == 'boost_draw_pile':
                                self.boost_draw_pile = keep_within(self.boost_draw_pile + addition, slider.min_value, slider.max_value)
                pygame.draw.rect(self.surface, slider.active_color, [slider.pos, slider.size])
            elif slider.color != -1:
                pygame.draw.rect(self.surface, slider.color, [slider.pos, slider.size])
            if slider.text_variable != '':
                variable_text = ''
                if slider.text_variable == 'volume':
                    slider.update_knob_pos(self.volume)
                    variable_text = slider.text.format(str(self.volume)[0:slider.text_variable_char_limit])
                elif slider.text_variable == 'boost_periodicity':
                    slider.update_knob_pos(self.boost_periodicity)
                    variable_text = slider.text.format(str(self.boost_periodicity)[0:slider.text_variable_char_limit])
                elif slider.text_variable == 'boost_draw_pile':
                    slider.update_knob_pos(self.boost_draw_pile)
                    variable_text = slider.text.format(str(self.boost_draw_pile)[0:slider.text_variable_char_limit])
                [slider.text_image, new_text_image_size] = self.text2img(variable_text, slider.text_color, slider.text_font, slider.text_size, slider.text_bold)
            if slider.text_image != None:
                self.surface.blit(slider.text_image, slider.text_pos)
            p = [slider.slider_pos[0], slider.slider_pos[1] + slider.slider_size[1] / 3]
            s = [slider.slider_size[0], slider.slider_size[1] / 3]
            pygame.draw.rect(self.surface, slider.right_color, [p, s])
            s = [slider.percent * slider.slider_size[0], slider.slider_size[1] / 3]
            pygame.draw.rect(self.surface, slider.left_color, [p, s])
            s = [0.08 * slider.slider_size[0], slider.slider_size[1]]
            p = [slider.slider_pos[0] + slider.percent * slider.slider_size[0] - 0.5 * s[0], slider.slider_pos[1]]
            pygame.draw.rect(self.surface, slider.knob_color, [p, s])

        # Find previous and new buttons the cursor is on
        for button in self.pages[self.page].buttons:
            if (self.cursor == button.button_pos) or (ocursor == button.button_pos):
                active_things.append(button)
        for lisk in self.pages[self.page].lists:
            if lisk.selectable:
                if self.cursor[0] == lisk.select_pos[0]:
                    if self.cursor[1] >= lisk.select_pos[1]:
                        list_length = len(self.players) * ((lisk.type == 'player') or (lisk.type == 'score')) + len(self.levels) * (lisk.type == 'level') + len(self.snake_scores) * (lisk.type == 'snake_score') + len(self.scythe_scores) * (lisk.type == 'scythe_score')
                        if self.cursor[1] < lisk.select_pos[1] + list_length:
                            active_things.append(lisk)
                if ocursor[0] == lisk.select_pos[0]:
                    if ocursor[1] >= lisk.select_pos[1]:
                        list_length = len(self.players) * ((lisk.type == 'player') or (lisk.type == 'score')) + len(self.levels) * (lisk.type == 'level') + len(self.snake_scores) * (lisk.type == 'snake_score') + len(self.scythe_scores) * (lisk.type == 'scythe_score')
                        if ocursor[1] < lisk.select_pos[1] + list_length:
                            active_things.append(lisk)
        for slider in self.pages[self.page].sliders:
            if (self.cursor == slider.button_pos) or (ocursor == slider.button_pos):
                active_things.append(slider)

        if self.cursor != ocursor:
            for thing in active_things:
                self.su_rects.append([thing.pos, thing.size])

        for control in self.pages[self.page].controls:
            if control.trigger != 'page_entrance' and control.trigger != 'continual_early':
                if self.menu_controls[control.trigger]:
                    self.do_actions(control.actions)
        
        if self.page == 'snake_results':
            if self.snake_game.score >= self.required_snake_score:
                self.show_secret()
        if self.page == 'scythe_results':
            if self.scythe_game.score >= self.required_scythe_score:
                self.show_secret()

    def load_levels(self):
        self.level_directory = os.path.join(self.cwd, 'levels')
        self.levels = {}
        for lv in os.listdir(self.level_directory):
            file = open(os.path.join(self.level_directory, lv), encoding = 'utf-8')
            self.levels[lv.replace('.txt', '')] = level(file.readlines(), lv.replace('.txt', ''))
            file.close()
        self.level = ''

    def initialize_level(self):
        self.mode_entrance = 1
        lvl = self.levels[self.level]
        self.reset_boosts()
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if i < len(lvl.player_poses):
                player_pos = lvl.player_poses[i]
            else:
                player_pos = [(3 * (i - len(lvl.player_poses)) * lvl.player_size[0]) % lvl.size[0], 0]
            ps = lvl.player_size[:]
            pg = lvl.player_gravity
            js = lvl.player_jump_strength
            vt = lvl.player_vel_terminal[:]
            dv = lvl.player_vel_delta[:]
            sh = lvl.player_shield_health_base
            sr = lvl.player_shield_regen
            if (plajer.name.lower() == 'sonic') and (plajer.base_color == 0x0000ff):
                vt[0] *= 2
                dv[0] *= 2
            elif (plajer.name.lower() == 'mario') and (plajer.base_color == 0xff0000):
                vt[1] *= 1.4
                js *= 1.4
            elif (plajer.name.lower() == 'luigi') and (plajer.base_color == 0x00cc00):
                vt[1] *= 1.6
                js *= 1.6
            elif (plajer.name.lower() == 'peach') and (plajer.base_color == 0xff8888):
                pg *= 0.1
            elif (plajer.name.lower() == 'yoshi') and (plajer.base_color == 0x00aa00):
                pg *= 0.2
                sh *= 4
                sr *= 6
            elif (plajer.name.lower() == 'pac man') and (plajer.base_color == 0xffff00):
                plajer.pac_dir = [0, 1]
                vt[0] *= 0.9
            elif (plajer.name.lower() == 'game and watch') and (plajer.base_color == 0x000000):
                plajer.gaw_adjustment = [0, 0]
                plajer.gaw_lpos = player_pos[:]
                plajer.gaw_llpos = player_pos[:]
                plajer.gaw_counter = [5, 5]
            elif (plajer.name.lower() == 'link') and (plajer.base_color == 0x008800):
                plajer.arrow_counter = 0
                plajer.arrow_counter_reset = 50
                plajer.arrows = []
                plajer.penetration_depth = 6
            elif (plajer.name.lower() == 'ness') and (plajer.base_color == 0x888800):
                plajer.fire_counter = 0
                plajer.fire_counter_reset = 35
                plajer.fire_life = 20
                plajer.fires = []
                plajer.penetration_depth = 6
            elif (plajer.name.lower() == 'pikachu') and (plajer.base_color == 0xffff00):
                plajer.zap_counter = 0
                plajer.zap_counter_reset = 65
                plajer.zaps = []
                plajer.penetration_depth = 6
            elif (plajer.name.lower() == 'bowser') and (plajer.base_color == 0xff9900):
                bowser_m = 2
                player_pos = [player_pos[0] - 0.5 * (bowser_m - 1) * ps[0], int(player_pos[1] - (bowser_m - 1) * ps[1])]
                ps = [bowser_m * ps[0], bowser_m * ps[1]]
                vt[0] *= 0.5
                dv[0] *= 0.5
                vt[1] *= 0.8
                js *= 0.8
                plajer.fire_counter = 0
                plajer.fire_counter_reset = 7
                plajer.fire_life = 20 * bowser_m
                plajer.fires = []
                plajer.penetration_depth = 6
            plajer.soft_reset(player_pos, ps, pg, js, vt, dv, sh, sr)
        pygame.mouse.set_visible(0)

    def get_level_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = 0
            elif ((event.type == pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE)) or ((event.type == pygame.JOYBUTTONDOWN) and (event.button == pygame.CONTROLLER_BUTTON_BACK)):
                if self.mode == 'squish':
                    self.do_actions([['goto', 'pause']])
                elif self.mode == 'tron':
                    self.do_actions([['goto', 'pause_tron']])
            elif (event.type == pygame.JOYDEVICEADDED) or (event.type == pygame.JOYDEVICEREMOVED):
                self.reset_joysticks()
            elif (event.type == pygame.WINDOWRESIZED) or (event.type == pygame.WINDOWMOVED) or (event.type == pygame.WINDOWEXPOSED):
                self.update_window_size()

        self.get_player_inputs()

    def get_player_inputs(self):
        # [Redact] this
        #if self.mode_entrance:
        #    self.load_cpu_weights()
        #    self.alter_cpu_weights()
        key = pygame.key.get_pressed()
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if not plajer.is_cpu:
                for control_key in plajer.controls:
                    plajer.controls[control_key][-2] = plajer.controls[control_key][-1]
                    control = plajer.controls[control_key][:]
                    if control[0] == -1:
                        plajer.controls[control_key][-1] = key[control[1]]
                    if len(self.controllers) > 0:
                        # This part causes 1 controller to control multiple players
                        # if there aren't enough controllers as assigned to the players
                        if control[0] >= len(self.controllers):
                            control[0] %= len(self.controllers)
                        if control[0] != -1:
                            if control[1] == 'button':
                                if self.joysticks[control[0]].get_numbuttons() > control[2]:
                                    plajer.controls[control_key][-1] = self.joysticks[control[0]].get_button(control[2])
                            elif control[1] == 'axis':
                                if self.joysticks[control[0]].get_numaxes() > control[2]:
                                    plajer.controls[control_key][-1] = (control[3] * self.joysticks[control[0]].get_axis(control[2]) >= self.joystick_threshold)
                            elif control[1] == 'hat':
                                if self.joysticks[control[0]].get_numhats() > control[2]:
                                    plajer.controls[control_key][-1] = (self.joysticks[control[0]].get_hat(control[2]) == control[3])
            elif self.mode == 'squish':
                self.get_cpu_inputs(i)
            elif self.mode == 'tron':
                self.get_tron_cpu_inputs(i)
            if self.mode == 'squish':
                if plajer.controls['up'][-1]:
                    plajer.controls['jump'][-1] = 1
                elif plajer.controls['jump'][-1]:
                    plajer.controls['up'][-1] = 1










    def set_cpu_weights(self):
        self.maintain_constant = 1000 # [Redact] Not being used
        self.past_ticks_constant = 300 # [Redact] Not being used
        self.giveup_ticks = 300 # [Redact] Not being used
        self.position_weight = 40

        self.run_player_weights = {'base'       : 1000,
                                   'scale'      : 10,
                                   'kill'       : 15,
                                   'skill'      : -15,
                                   'speed'      : 8,
                                   'sinvincible': -15,
                                   'dx'         : -1500,
                                   'dy'         : -1000,
                                   'above'      : 50}
        
        self.pursue_player_weights = {'base'       : 1000,
                                      'scale'      : 15,
                                      'skill'      : 20,
                                      'kill'       : -10,
                                      'sspeed'     : 12,
                                      'speed'      : -5,
                                      'sjump'      : 8,
                                      'jump'       : -5,
                                      'sinvincible': 9,
                                      'invincible' : -5,
                                      'sphase'     : 4,
                                      'phase'      : -3,
                                      'dx'         : -1500,
                                      'dy'         : -1000,
                                      'above'      : -40}

        self.pursue_boost_weights = {'base'       : 1000,
                                     'scale'      : 1,
                                     'skill'      : -3,
                                     'sspeed'     : -4,
                                     'sjump'      : -4,
                                     'sinvincible': -3,
                                     'sphase'     : -6,
                                     'dx'         : -2000,
                                     'dy'         : -1500,
                                     'above'      : -5,
                                     'voidance'   : -350}

        self.void_detect_width = 0.01
        # [Redact] this, it isn't being used anymore
        self.void_weights = {'base'  : 500,
                             'scale' : -100,
                             'sspeed': -100,
                             'sjump' : -700,
                             'dy'    : -0.01,
                             'vy'    : 1000}

    # The following 4 functions are for cpu training
    # [Redact] this
    def load_cpu_weights(self):
        # Read g file and set weights
        self.cpd = os.path.join(self.cwd, 'cpu_weights')
        cpf = os.listdir(self.cpd)
        self.file_val = len(cpf)
        cp = cpf[-1]
        file = open(os.path.join(self.cpd, cp), encoding = 'utf-8')
        di = ''
        for line in file.readlines():
            line = line.replace('\n', '')
            sl = line.split('=')
            pr = sl[0]
            if len(sl) > 1:
                val = sl[1]
            if pr == 'maintain_constant':
                self.maintain_constant = float(val)
            elif pr == 'past_ticks_constant':
                self.past_ticks_constant = float(val)
            elif pr == 'giveup_ticks':
                self.giveup_ticks = float(val)
            elif pr == 'position_weight':
                self.position_weight = float(val)
            elif pr == 'run_player_weights':
                di = self.run_player_weights
            elif pr == 'void_weights':
                di = self.void_weights
            elif pr == 'pursue_player_weights':
                di = self.pursue_player_weights
            elif pr == 'pursue_boost_weights':
                di = self.pursue_boost_weights
            for key in [*self.run_player_weights] + [*self.void_weights] + [*self.pursue_player_weights] + [*self.pursue_boost_weights]:
                if pr == key:
                    di[key] = float(val)
        file.close()

    # [Redact] this
    def alter_cpu_weights(self):
        mu1 = 1
        si1 = 0.1
        mu2 = 0
        si2 = 5
        draw_pile = 2
        # Give the weights to each player with random adjustments
        for plajer in self.players:
            if plajer.is_cpu:
                if random.randint(0, draw_pile) == 0:
                    plajer.maintain_constant = self.maintain_constant * random.gauss(mu1, si1) + random.gauss(mu2, si2)
                else:
                    plajer.maintain_constant = self.maintain_constant
                if random.randint(0, draw_pile) == 0:
                    plajer.past_ticks_constant = self.past_ticks_constant * random.gauss(mu1, si1) + random.gauss(mu2, si2)
                else:
                    plajer.past_ticks_constant = self.past_ticks_constant
                if random.randint(0, draw_pile) == 0:
                    plajer.giveup_ticks = self.giveup_ticks * random.gauss(mu1, si1) + random.gauss(mu2, si2)
                else:
                    plajer.giveup_ticks = self.giveup_ticks
                if random.randint(0, draw_pile) == 0:
                    plajer.position_weight = self.position_weight * random.gauss(mu1, si1) + random.gauss(mu2, si2)
                else:
                    plajer.position_weight = self.position_weight

                plajer.run_player_weights = {}
                for key in self.run_player_weights:
                    if random.randint(0, draw_pile) == 0:
                        plajer.run_player_weights[key] = self.run_player_weights[key] * random.gauss(mu1, si1) + random.gauss(mu2, si2)
                    else:
                        plajer.run_player_weights[key] = self.run_player_weights[key]
                plajer.void_weights = {}
                for key in self.void_weights:
                    if random.randint(0, draw_pile) == 0:
                        plajer.void_weights[key] = self.void_weights[key] * random.gauss(mu1, si1) + random.gauss(mu2, si2)
                    else:
                        plajer.void_weights[key] = self.void_weights[key]
                plajer.pursue_player_weights = {}
                for key in self.pursue_player_weights:
                    if random.randint(0, draw_pile) == 0:
                        plajer.pursue_player_weights[key] = self.pursue_player_weights[key] * random.gauss(mu1, si1) + random.gauss(mu2, si2)
                    else:
                        plajer.pursue_player_weights[key] = self.pursue_player_weights[key]
                plajer.pursue_boost_weights = {}
                for key in self.pursue_boost_weights:
                    if random.randint(0, draw_pile) == 0:
                        plajer.pursue_boost_weights[key] = self.pursue_boost_weights[key] * random.gauss(mu1, si1) + random.gauss(mu2, si2)
                    else:
                        plajer.pursue_boost_weights[key] = self.pursue_boost_weights[key]

    # [Redact] this
    def set_as_cpu_weights(self, plajer):
        # Set this plajers weights as the defualt ones
        pl = plajer
        self.maintain_constant = pl.maintain_constant
        self.past_ticks_constant = pl.past_ticks_constant
        self.giveup_ticks = pl.giveup_ticks
        self.position_weight = pl.position_weight

        for key in self.run_player_weights:
            self.run_player_weights[key] = pl.run_player_weights[key]
        for key in self.void_weights:
            self.void_weights[key] = pl.void_weights[key]
        for key in self.pursue_player_weights:
            self.pursue_player_weights[key] = pl.pursue_player_weights[key]
        for key in self.pursue_boost_weights:
            self.pursue_boost_weights[key] = pl.pursue_boost_weights[key]

    # [Redact] this
    def save_cpu_weights(self):
        # Save the winner's weights as a g# file if the winner is a cpu
        pl = self.players[self.winner_index]
        if pl.is_cpu:
            cpf = os.listdir(self.cpd)
            self.file_val = len(cpf)
            file_name = 'g' + '0' * (self.file_val < 1000) + '0' * (self.file_val < 100) + '0' * (self.file_val < 10) + '0' * (self.file_val < 1) + str(self.file_val) + '.txt'
            file = open(os.path.join(self.cpd, file_name), mode = 'w', encoding = 'utf-8')
            file.write('maintain_constant=' + str(pl.maintain_constant))
            file.write('\npast_ticks_constant=' + str(pl.past_ticks_constant))
            file.write('\ngiveup_ticks=' + str(pl.giveup_ticks))
            file.write('\nposition_weight=' + str(pl.position_weight))
            file.write('\n\nrun_player_weights')
            for key in pl.run_player_weights:
                file.write('\n' + key + '=' + str(pl.run_player_weights[key]))
            file.write('\n\nvoid_weights')
            for key in pl.void_weights:
                file.write('\n' + key + '=' + str(pl.void_weights[key]))
            file.write('\n\npursue_player_weights')
            for key in pl.pursue_player_weights:
                file.write('\n' + key + '=' + str(pl.pursue_player_weights[key]))
            file.write('\n\npursue_boost_weights')
            for key in pl.pursue_boost_weights:
                file.write('\n' + key + '=' + str(pl.pursue_boost_weights[key]))
            file.close()




    def get_cpu_inputs(self, i):
        # Set player and level values and reset player controls
        plajer = self.players[i]
        tarjet = plajer.target
        for control_key in plajer.controls:
            plajer.controls[control_key][-2] = plajer.controls[control_key][-1]
            plajer.controls[control_key][-1] = 0
        lvl = self.levels[self.level]

        # Record new position and calculate short and long average positions (NOTE: Maybe don't need this for anything)
        plajer.average_trail[plajer.average_trail_index] = plajer.pos[:]
        plajer.average_trail_index = (plajer.average_trail_index + 1) % len(plajer.average_trail)
        p_total = [0, 0]
        p2_total = [0, 0]
        offset = [0, 0]
        if lvl.horizontal_looping:
            offset[0] = lvl.size[0] - (plajer.short_average_pos[0] + 0.5 * lvl.size[0]) % lvl.size[0]
        if lvl.vertical_looping:
            offset[1] = lvl.size[1] - (plajer.short_average_pos[1] + 0.5 * lvl.size[1]) % lvl.size[1]
        for ii in range(0, len(plajer.average_trail)):
            if lvl.horizontal_looping:
                p_total[0] += (plajer.average_trail[ii][0] + offset[0]) % lvl.size[0]
            else:
                p_total[0] += plajer.average_trail[ii][0]
            if lvl.vertical_looping:
                p_total[1] += (plajer.average_trail[ii][1] + offset[1]) % lvl.size[1]
            else:
                p_total[1] += plajer.average_trail[ii][1]
            if ii == round(len(plajer.average_trail) / 2 - 1):
                p2_total = p_total[:]
        
        plajer.long_average_pos = [p_total[0] / len(plajer.average_trail), p_total[1] / len(plajer.average_trail)]
        plajer.short_average_pos = [p2_total[0] / round(len(plajer.average_trail) / 2), p2_total[1] / round(len(plajer.average_trail) / 2)]
        if lvl.horizontal_looping:
            plajer.long_average_pos[0] = (plajer.long_average_pos[0] - offset[0]) % lvl.size[0]
            plajer.short_average_pos[0] = (plajer.short_average_pos[0] - offset[0]) % lvl.size[0]
        if lvl.horizontal_looping:
            plajer.long_average_pos[1] = (plajer.long_average_pos[1] - offset[1]) % lvl.size[1]
            plajer.short_average_pos[1] = (plajer.short_average_pos[1] - offset[1]) % lvl.size[1]

        #NOTE
        
        self.dba1 = plajer.short_average_pos
        self.dba2 = plajer.long_average_pos

        self.tar = plajer.target
        self.plajer_pos = plajer.pos

        # Tick present target
        tarjet.ticks += 1
        # Untick failed targets and remove once ticks reaches 0
        remove_old_targets = []
        for ti in range(0, len(plajer.failed_targets)):
            ftarget = plajer.failed_targets[ti]
            ftarget.ticks -= 1
            if ftarget.ticks <= 0:
                remove_old_targets.append(ti)
        remove_old_targets.sort(reverse = 1)
        for ti in remove_old_targets:
            plajer.failed_targets.pop(ti)
        
        # Check if void target has been reached
        if plajer.target_void:
            plajer.target_void.ticks += 1
            if plajer.target_void.check_satisfied(lvl, self.boosts) or (random.random() < (1 - 1 / (1 + 0.0005 * plajer.target_void.ticks))):
                plajer.last_void = plajer.target_void.ticks
                plajer.target_void = None
        elif plajer.last_void > 0:
            plajer.last_void -= 15
            if plajer.last_void < 0:
                plajer.last_void = 0

        # Check if target has been reached or killed
        tarjet.check_satisfied(lvl, self.boosts)

        # Possibly check if a new target should be selected
        # If the present target has been pursued for a long time then be more likely to change
        if random.random() < (1 - 1 / (1 + 0.001 * tarjet.ticks)):
            # If the last target was failed then append the last target to failed target list
            if not tarjet.satisfied:
                plajer.failed_targets.append(tarjet)

            potential_targets = []

            # Assess all alive players on opposing team to flee and pursue
            for ii, plaier in enumerate(self.players):
                if (i != ii) and plaier.alive and ((self.team_count <= 0) or (plajer.team != plaier.team)):
                    # Add weights for fleeing the player
                    weight = self.run_player_weights['base']
                    weight += self.run_player_weights['kill'] * plaier.boosts['kill']
                    weight += self.run_player_weights['skill'] * plajer.boosts['kill']
                    weight += self.run_player_weights['speed'] * plaier.boosts['speed']
                    weight += self.run_player_weights['sinvincible'] * plajer.boosts['invincible']
                    p1 = plajer.center(lvl)
                    p2 = plaier.center(lvl)
                    dx = abs(p1[0] - p2[0])
                    if lvl.horizontal_looping:
                        dx %= (0.5 * lvl.size[0])
                    dy = abs(p1[1] - p2[1])
                    if lvl.vertical_looping:
                        dy %= (0.5 * lvl.size[1])
                    above = p1[1] - p2[1]
                    if lvl.vertical_looping:
                        if abs(above) > 0.5 * lvl.size[1]:
                            above = (above + 0.5 * lvl.size[1]) % lvl.size[1] - 0.5 * lvl.size[1]
                    weight += self.run_player_weights['dx'] * dx / lvl.size[0]
                    weight += self.run_player_weights['dy'] * dy / lvl.size[1]
                    # A player above the cpu is a much greater threat
                    abv = above / lvl.size[1]
                    if abv != 0:
                        weight += self.run_player_weights['above'] / abv
                    weight /= (self.run_player_weights['scale'] + 0.01 * (self.run_player_weights['scale'] == 0))
                    weight /= (plajer.enemy_count + 0.01 * (plajer.enemy_count == 0))
                    potential_targets.append(target(plajer, weight, 'player', 0, plaier, lvl))

                    # Add weights for pursuing the player
                    weight = self.pursue_player_weights['base']
                    weight += self.pursue_player_weights['skill'] * plajer.boosts['kill']
                    weight += self.pursue_player_weights['kill'] * plaier.boosts['kill']
                    weight += self.pursue_player_weights['sspeed'] * plajer.boosts['speed']
                    weight += self.pursue_player_weights['speed'] * plaier.boosts['speed']
                    weight += self.pursue_player_weights['sjump'] * plajer.boosts['jump']
                    weight += self.pursue_player_weights['jump'] * plaier.boosts['jump']
                    weight += self.pursue_player_weights['sinvincible'] * plajer.boosts['invincible']
                    weight += self.pursue_player_weights['invincible'] * plaier.boosts['invincible']
                    weight += self.pursue_player_weights['sphase'] * plajer.boosts['phase']
                    weight += self.pursue_player_weights['phase'] * plaier.boosts['phase']
                    p1 = plajer.center(lvl)
                    p2 = plaier.center(lvl)
                    dx = abs(p1[0] - p2[0])
                    if lvl.horizontal_looping:
                        dx %= (0.5 * lvl.size[0])
                    dy = abs(p1[1] - p2[1])
                    if lvl.vertical_looping:
                        dy %= (0.5 * lvl.size[1])
                    above = p1[1] - p2[1]
                    if lvl.vertical_looping:
                        if abs(above) > 0.5 * lvl.size[1]:
                            above = (above + 0.5 * lvl.size[1]) % lvl.size[1] - 0.5 * lvl.size[1]
                    weight += self.pursue_player_weights['dx'] * dx / lvl.size[0]
                    weight += self.pursue_player_weights['dy'] * dy / lvl.size[1]
                    abv = above / lvl.size[1]
                    if abv != 0:
                        weight += self.pursue_player_weights['above'] / abv
                    weight /= self.pursue_player_weights['scale']
                    weight /= (plajer.enemy_count + 0.01 * (plajer.enemy_count == 0))
                    potential_targets.append(target(plajer, weight, 'player', 1, plaier, lvl))
            
            # Assess boosts to pursue
            if plajer.alive:
                for boost in self.boosts:
                    # Add weights for pursuing the boost
                    weight = self.pursue_boost_weights['base']
                    for boost_type in self.boost_types:
                        if boost[1] == boost_type:
                            weight += self.pursue_boost_weights['s' + boost_type] * plajer.boosts[boost_type]
                            break
                    p1 = plajer.center(lvl)
                    p2 = boost[0]
                    dx = abs(p1[0] - p2[0])
                    if lvl.horizontal_looping:
                        dx %= (0.5 * lvl.size[0])
                    dy = abs(p1[1] - p2[1])
                    if lvl.vertical_looping:
                        dy %= (0.5 * lvl.size[1])
                    above = p1[1] - p2[1]
                    if lvl.vertical_looping:
                        if abs(above) > 0.5 * lvl.size[1]:
                            above = (above + 0.5 * lvl.size[1]) % lvl.size[1] - 0.5 * lvl.size[1]
                    voidy = boost[0][1]
                    weight += self.pursue_boost_weights['dx'] * dx / lvl.size[0]
                    weight += self.pursue_boost_weights['dy'] * dy / lvl.size[1]
                    abv = above / lvl.size[1]
                    if abv != 0:
                        weight += self.pursue_boost_weights['above'] / abv
                    if boost[2]:
                        weight += self.pursue_boost_weights['voidance'] * voidy / lvl.size[1]
                    weight /= (self.pursue_boost_weights['scale'] + 0.01 * (self.pursue_boost_weights['scale'] == 0))
                    weight /= len(self.boosts)
                    potential_targets.append(target(plajer, weight, 'boost', 1, boost))
            
            # Pick a random position
            if lvl.vertical_looping:
                p = [random.randint(0, lvl.size[0] - 1), random.randint(0, lvl.size[1] - 1)]
            else:
                p = [random.randint(0, lvl.size[0] - 1), (random.random() ** 2) * lvl.size[1]]
            potential_targets.append(target(plajer, self.position_weight, 'position', 1, p))

            # Pick a new target
            wotal = 0
            windeces = []
            wadex = []
            waddex = []
            for wi, potential_target in enumerate(potential_targets):
                # Lower the weights of failed targets
                for wii, failed_target in enumerate(plajer.failed_targets):
                    if (potential_target.target == failed_target.target) and (potential_target.dir == failed_target.dir):
                        potential_target.weight *= 1 / (1 + 0.01 * failed_target.ticks)
                        wadex.append(wi)
                        waddex.append(wii)
                        break
                # Create a list for weighted random choice
                if potential_target.weight <= 0:
                    potential_target.weight = 0
                wotal += potential_target.weight
                windeces.append(wotal)

            # Choose from the weighted random values
            wandom = random.random() * wotal
            for windex, weight in enumerate(windeces):
                if wandom < weight:
                    plajer.target = potential_targets[windex]
                    break
            
            # Remove the new chosen target from failed targets if needed
            if waddex.count(windex):
                plajer.failed_targets.pop(waddex.index(windex))
            #NOTE
            self.pot_tar = potential_targets

        # Check if the void is a danger and avoid appropriately
        if not lvl.vertical_looping and not plajer.target_void:
            # If the player ran from the void recently don't fear the void
            if random.random() < (1 / (1 + 5 * plajer.last_void)):
                # If the player has a healthy jump boost it is unlikely to fear the void
                if random.random() < 1 / (1 + 2 * plajer.boosts['jump']):
                    # If the player is traveling upwards it is less likely to fear the void
                    if random.random() < 1 / (1 + 1 / (math.exp(plajer.vel[1] + 0.2 * plajer.vel_terminal[1]))):
                        # Check if there is a block below the player
                        block_below = 0
                        s1 = [self.void_detect_width * plajer.size[0], lvl.size[1] - plajer.pos[1]]
                        p1 = [plajer.pos[0] + 0.5 * (1 - self.void_detect_width) * plajer.size[0], plajer.pos[1] + plajer.size[1]]
                        for block in lvl.blocks:
                            if block.solid:
                                overlap = rect_overlap(p1, s1, [0, 0], block.pos, block.size, lwl = lvl)
                                if overlap != [0, 0]:
                                    block_below = 1
                                    break
                        
                        # At this point if there is no block below then the player should fear the void
                        if not block_below:
                            rs = []
                            ps = []
                            p1 = plajer.center(lvl)
                            # Find a spot beside or above the closest block that is below the player
                            for block in lvl.blocks:
                                if block.solid:
                                    cc = []
                                    cc.append([block.pos[0], block.pos[1] + block.size[1]])
                                    cc.append([block.pos[0] + block.pos[1], block.pos[1] + block.size[1]])
                                    for c in cc:
                                        if lvl.horizontal_looping:
                                            # Make the corners the nearest to the player
                                            shift = p1[0] - 0.5 * lvl.size[0]
                                            c[0] = (c[0] - shift) % lvl.size[0] + shift
                                        # Test if the corner is reachable
                                        if c[1] >= abs(c[0] - p1[0]) - (0.37 * (c[0] - p1[0]) * (plajer.vel[0] / plajer.vel_terminal[0])) + p1[1]:
                                            rs.append(distance(p1, c, lvl))
                                            pa = [c[0], c[1] - block.size[1] - 0.5 * plajer.size[1]]
                                            ps.append(pa)
                            
                            if not len(rs):
                                # Find the nearest block
                                for block in lvl.blocks:
                                    if block.solid:
                                        pc = [block.pos[0] + 0.5 * block.size[0], block.pos[1] + 0.5 * block.size[1]]
                                        rs.append(distance(p1, pc, lvl))
                                        pa = [pc[0], block.pos[1] - 0.5 * plajer.size[1]]
                                        ps.append(pa)
                            
                            # Pick the appropriate position to go to
                            windex = None
                            smalldex = lvl.size[0] ** 2 + lvl.size[1] ** 2
                            for wi, radius in enumerate(rs):
                                if radius < smalldex:
                                    smalldex = radius
                                    windex = wi
                            if windex != None:
                                plajer.target_void = target(plajer, 0, 'position', 1, ps[windex])
                                plajer.target.ticks += 500



        
        # Respond if alive and being squished
        pushing = 0
        if plajer.alive and (plajer.squish_width != 1):
            # Push against the player
            if not plajer.block_on_side[0] and not plajer.block_on_side[1]:
                if random.randint(0, 1):
                    pushing = 1
                    plajer.controls['left'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
                else:
                    pushing = 1
                    plajer.controls['right'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
            elif not plajer.block_on_side[0]:
                pushing = 1
                plajer.controls['left'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
            elif not plajer.block_on_side[1]:
                pushing = 1
                plajer.controls['right'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
            
            # Try jumping away
            plajer.controls['jump'][-1] = (random.randint(1, plajer.input_success_pile) == 1)
            
            # Try phasing
            if plajer.squish_width <= 0.8:
                plajer.controls['ability'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)

            # Try shielding
            if plajer.squish_width <= 0.5:
                plajer.controls['shield'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)

        # Manage inputs
        p1 = plajer.center(lvl)
        if plajer.target_void:
            p2 = plajer.target_void.pos
        else:
            p2 = plajer.target.pos
        dx = p2[0] - p1[0]
        if lvl.horizontal_looping:
            dx = (dx + 0.5 * lvl.size[0]) % lvl.size[0] - 0.5 * lvl.size[0]
        dy = p2[1] - p1[1]
        if lvl.vertical_looping:
            dy = (dy + 0.5 * lvl.size[1]) % lvl.size[1] - 0.5 * lvl.size[1]
        
        if plajer.target_void or plajer.target.dir:
            # Pursue the target position
            if plajer.target_void:
                plajer.controls['jump'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
            elif dy < plajer.size[1]:
                plajer.controls['jump'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
            if not pushing:
                if dx < 0:
                    plajer.controls['left'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
                elif dx > 0:
                    plajer.controls['right'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
                else:
                    if random.randint(0, 1):
                        plajer.controls['left'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
                    else:
                        plajer.controls['right'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
        else:
            # Flee from the target position
            if dy >= 0:
                plajer.controls['jump'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
            elif not lvl.vertical_looping:
                if plajer.pos[1] + plajer.size[1] > 0.98 * lvl.size[1]:
                    plajer.controls['jump'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
            if not pushing:
                if dx > 0:
                    plajer.controls['left'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
                elif dx < 0:
                    plajer.controls['right'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
                else:
                    if random.randint(0, 1):
                        plajer.controls['left'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)
                    else:
                        plajer.controls['right'][-1] = (random.randint(1, plajer.input_noise_pile) != 1)

    # [Redact] this
    def old_get_cpu_inputs(self, i):
        plajer = self.players[i]
        self.set_as_cpu_weights(plajer)
        for control_key in plajer.controls:
            plajer.controls[control_key][-2] = plajer.controls[control_key][-1]
            plajer.controls[control_key][-1] = 0
        lvl = self.levels[self.level]
        
        plajer.average_trail[plajer.average_trail_index] = plajer.pos[:]
        plajer.average_trail_index = (plajer.average_trail_index + 1) % len(plajer.average_trail)
        p_total = [0, 0]
        p2_total = [0, 0]
        offset = [0, 0]
        if lvl.horizontal_looping:
            offset[0] = lvl.size[0] - (plajer.short_average_pos[0] + 0.5 * lvl.size[0]) % lvl.size[0]
        if lvl.vertical_looping:
            offset[1] = lvl.size[1] - (plajer.short_average_pos[1] + 0.5 * lvl.size[1]) % lvl.size[1]
        for ii in range(0, len(plajer.average_trail)):
            if lvl.horizontal_looping:
                p_total[0] += (plajer.average_trail[ii][0] + offset[0]) % lvl.size[0]
            else:
                p_total[0] += plajer.average_trail[ii][0]
            if lvl.vertical_looping:
                p_total[1] += (plajer.average_trail[ii][1] + offset[1]) % lvl.size[1]
            else:
                p_total[1] += plajer.average_trail[ii][1]
            if ii == round(len(plajer.average_trail) / 2 - 1):
                p2_total = p_total[:]
        
        plajer.long_average_pos = [p_total[0] / len(plajer.average_trail), p_total[1] / len(plajer.average_trail)]
        plajer.short_average_pos = [p2_total[0] / round(len(plajer.average_trail) / 2), p2_total[1] / round(len(plajer.average_trail) / 2)]
        if lvl.horizontal_looping:
            plajer.long_average_pos[0] = (plajer.long_average_pos[0] - offset[0]) % lvl.size[0]
            plajer.short_average_pos[0] = (plajer.short_average_pos[0] - offset[0]) % lvl.size[0]
        if lvl.horizontal_looping:
            plajer.long_average_pos[1] = (plajer.long_average_pos[1] - offset[1]) % lvl.size[1]
            plajer.short_average_pos[1] = (plajer.short_average_pos[1] - offset[1]) % lvl.size[1]

        p1 = plajer.pos
        p2 = plajer.short_average_pos
        self.dba1 = plajer.short_average_pos
        self.dba2 = plajer.long_average_pos
        if lvl.horizontal_looping:
            dx = abs(p1[0] - p2[0])
            if dx > 0.5 * lvl.size[0]:
                dx = abs(dx - lvl.size[0])
            r = distance([dx, p1[1]], [0, p2[1]])
        else:
            r = distance(p1, p2)
        if r < 0.5 * (plajer.base_size[0] + plajer.base_size[1]):
            plajer.target[0] = 0

        # Entry format: [weight, target_towards, target_type, target]
        potential_targets = []
        # Reasons to run
        for ii in range(0, len(self.players)):
            if ii != i:
                plaier = self.players[ii]
                if plaier.alive and not ((self.team_count > 0) and (plaier.team == plajer.team)):
                    weight = self.run_player_weights['base']
                    weight += self.run_player_weights['kill'] * plaier.boosts['kill']
                    weight += self.run_player_weights['speed'] * plaier.boosts['speed']
                    weight += self.run_player_weights['sinvincible'] * plajer.boosts['invincible']
                    p1 = plajer.center(lvl)
                    p2 = plaier.center(lvl)
                    dx = abs(p1[0] - p2[0])
                    if lvl.horizontal_looping:
                        dx %= (0.5 * lvl.size[0])
                    dy = abs(p1[1] - p2[1])
                    if lvl.vertical_looping:
                        dy %= (0.5 * lvl.size[1])
                    above = p1[1] - p2[1]
                    if above < 0.85 * plajer.base_size[1]:
                        if lvl.vertical_looping:
                            above += lvl.size[1]
                    dx += 0.01 * (dx == 0)
                    dy += 0.01 * (dy == 0)
                    above += 0.01 * (above == 0)
                    weight += self.run_player_weights['dx'] / dx
                    weight += self.run_player_weights['dy'] / dy
                    # A player above the cpu is a much greater threat
                    weight += self.run_player_weights['above'] / above
                    weight /= self.run_player_weights['scale']
                    entry = [weight, 0, 'player', plaier]
                    potential_targets.append(entry)
        
        # Detect void danger
        if not lvl.vertical_looping:
            block_below = 0
            s1 = [0.1 * plajer.size[0], lvl.size[1] - plajer.pos[1]]
            p1 = [plajer.pos[0] + 0.45 * plajer.size[0], plajer.pos[1] + plajer.size[1]]
            for block in lvl.blocks:
                if block.solid:
                    overlap = rect_overlap(p1, s1, [0, 0], block.pos, block.size, lwl = lvl)
                    if overlap != [0, 0]:
                        block_below = 1
                        break
            jumped = 0
            if (not block_below) and (plajer.vel[1] > 0) and (plajer.pos[1] / lvl.size[1] > 0.7):
                jumped = (random.randint(0, 3) == 0)
                plajer.controls['jump'][-1] = jumped * (random.randint(0, plajer.input_noise_pile) != 0)
            if not jumped:
                if (not block_below) and (plajer.vel[1] >= 0):
                    jumped = (random.randint(0, 2) == 0)
                    plajer.controls['jump'][-1] = jumped * (random.randint(0, plajer.input_noise_pile) != 0)
            # Only detect if there is a clear line of sight to the void
            if (not block_below) and (not plajer.on_ground):
                p1 = [plajer.pos[0] + 0.5 * plajer.size[0], lvl.size[1]]
                ps = []
                rs = []
                for block in lvl.blocks:
                    if block.solid:
                        p2 = [block.pos[0] + 0.5 * block.size[0], block.pos[1] + 0.5 * block.size[1]]
                        if lvl.horizontal_looping:
                            dx = abs(p1[0] - p2[0])
                            if dx > 0.5 * lvl.size[0]:
                                dx = abs(dx - lvl.size[0])
                            r = distance([dx, p1[1]], [0, p2[1]])
                        else:
                            r = distance(p1, p2)
                        ps.append(p2)
                        rs.append(r)
                ii = rs.index(min(rs))
                p = ps[ii]
                weight = self.void_weights['base']
                weight += self.void_weights['sspeed'] * plajer.boosts['speed']
                weight += self.void_weights['sjump'] * plajer.boosts['jump']
                weight += self.void_weights['vy'] * plajer.vel[1]
                dy = lvl.size[1] - plajer.pos[1]
                dy += 0.01 * (dy == 0)
                weight += self.void_weights['dy'] / dy
                weight /= self.void_weights['scale']
                entry = [weight, 1, 'position', p]
                potential_targets.append(entry)
            elif plajer.target[2] == 'position':
                plajer.target[0] = 0
        
        alive_players = 0
        for ii in range(0, len(self.players)):
            if ii != i:
                alive_players += self.players[ii].alive
        alive_players += (alive_players == 0)

        # Players to pursue
        for ii, plaier in enumerate(self.players):
            if ii != i:
                if plaier.alive and not ((self.team_count > 0) and (plaier.team == plajer.team)):
                    weight = self.pursue_player_weights['base']
                    weight += self.pursue_player_weights['skill'] * plajer.boosts['kill']
                    weight += self.pursue_player_weights['kill'] * plaier.boosts['kill']
                    weight += self.pursue_player_weights['sspeed'] * plajer.boosts['speed']
                    weight += self.pursue_player_weights['speed'] * plaier.boosts['speed']
                    weight += self.pursue_player_weights['sjump'] * plajer.boosts['jump']
                    weight += self.pursue_player_weights['jump'] * plaier.boosts['jump']
                    weight += self.pursue_player_weights['sinvincible'] * plajer.boosts['invincible']
                    weight += self.pursue_player_weights['invincible'] * plaier.boosts['invincible']
                    weight += self.pursue_player_weights['sphase'] * plajer.boosts['phase']
                    weight += self.pursue_player_weights['phase'] * plaier.boosts['phase']
                    p1 = plajer.center(lvl)
                    p2 = plaier.center(lvl)
                    dx = abs(p1[0] - p2[0])
                    if lvl.horizontal_looping:
                        dx %= (0.5 * lvl.size[0])
                    dx = dx / lvl.size[0]
                    dy = abs(p1[1] - p2[1])
                    if lvl.vertical_looping:
                        dy %= (0.5 * lvl.size[1])
                    dy = dy / lvl.size[1]
                    above = p1[1] - p2[1]
                    if above < 0.85 * plajer.base_size[1]:
                        if lvl.vertical_looping:
                            above += 0.5 * lvl.size[1]
                    weight += self.pursue_player_weights['dx'] * dx
                    weight += self.pursue_player_weights['dy'] * dy
                    weight += self.pursue_player_weights['above'] * above
                    weight /= self.pursue_player_weights['scale']
                    weight /= alive_players
                    entry = [weight, 1, 'player', plaier]
                    potential_targets.append(entry)

        for boost in self.boosts:
            if plajer.alive:
                weight = self.pursue_boost_weights['base']
                for boost_type in self.boost_types:
                    if boost[1] == boost_type:
                        weight += self.pursue_boost_weights['s' + boost_type] * plajer.boosts[boost_type]
                        break
                p1 = plajer.center(lvl)
                p2 = boost[0]
                dx = abs(p1[0] - p2[0])
                if lvl.horizontal_looping:
                    dx %= (0.5 * lvl.size[0])
                dy = abs(p1[1] - p2[1])
                if lvl.vertical_looping:
                    dy %= (0.5 * lvl.size[1])
                above = p1[1] - p2[1]
                if above < 0.85 * plajer.base_size[1]:
                    if lvl.vertical_looping:
                        above += lvl.size[1]
                dx += 0.01 * (dx == 0)
                dy += 0.01 * (dy == 0)
                voidy = boost[0][1] / lvl.size[1]
                weight += self.pursue_boost_weights['dx'] / dx
                weight += self.pursue_boost_weights['dy'] / dy
                weight += self.pursue_player_weights['above'] * above
                weight += self.pursue_boost_weights['voidance'] * voidy
                weight /= self.pursue_boost_weights['scale']
                weight /= (len(self.boosts) + (len(self.boosts) == 0))
                entry = [weight, 1, 'boost', boost]
                potential_targets.append(entry)
        
        # This needs heavy weight
        # See how far the void is from the cpu
        # See direction the cpu is going
        # See if there is a block below the cpu
        # See if there is a block to target onto and how far it is
        # Do this 3 or so times with different target blocks to go to



        #       Unless cpu has kill or invincibility boost with enough health
        #           Close player with kill boosts
        #           Close player above in position to squish the cpu
        #       Might fall in the void
        # Targets to pursue

        entry = [0, 1, 'maintain', plajer.target]
        if plajer.target_ticks == -1:
            entry[0] = 0
        else:
            if plajer.target_ticks > self.giveup_ticks:
                dx = abs(plajer.pos[0] - plajer.short_average_pos[0])
                dy = abs(plajer.pos[1] - plajer.short_average_pos[1])
                if lvl.horizontal_looping:
                    if dx > 0.5 * lvl.size[0]:
                        dx = abs(lvl.size[0] - dx)
                if lvl.vertical_looping:
                    if dy > 0.5 * lvl.size[1]:
                        dy = abs(lvl.size[1] - dy)
                if (dx == 0) and (dy == 0):
                    m = 0
                else:
                    m = -1 / ((dx ** 2 + dy ** 2) ** 0.5) + 1
                    #print(m)
            else:
                m = 1
            entry[0] = m * self.maintain_constant * plajer.target[0] / ((plajer.target_ticks + (plajer.target_ticks == 0))** 0.5)
            #print(entry[0])
        potential_targets.append(entry)

        # Decide if a new target is needed
        total = 0
        indexer = []
        iindeces = []
        for target in potential_targets:
            past_ticks = None
            for ii in range(0, len(plajer.past_targets)):
                tarjet = plajer.past_targets[ii]
                if tarjet[0][1:] == target[1:]:
                    past_ticks = tarjet[1]
                    iindeces.append(ii)
                    break
            if past_ticks != None:
                past_ticks += 0.01 * (past_ticks == 0)
                target[0] *= self.past_ticks_constant / past_ticks
            if target[0] > 0:
                total += target[0]
            indexer.append(total)
        ri = random.random() * total
        for i in range(0, len(indexer)):
            value = indexer[i]
            if ri < value:
                break
        if potential_targets[i][2] != 'maintain':
            if plajer.past_targets.count(plajer.target) == 0:
                plajer.past_targets.append([plajer.target[:], plajer.target_ticks])
            for ii in iindeces:
                if plajer.past_targets[ii][0][1:] == potential_targets[i][1:]:
                    plajer.past_targets.pop(ii)
                    break
            plajer.target = potential_targets[i]
            plajer.target_ticks = 0
            #print("Changed")
        plajer.target_ticks += 1
        
        self.db = potential_targets
        self.dbt = plajer.target
        self.dbp = plajer.pos

        # Path find to the target
        target = plajer.target
        p1 = plajer.center(lvl)
        if target[2] == 'player':
            p2 = target[3].center(lvl)
        elif target[2] == 'boost':
            p2 = target[3][0]
        elif target[2] == 'position':
            p2 = target[3]
        else:
            p2 = p1
        dx = p2[0] - p1[0]
        if lvl.horizontal_looping:
            dx = (dx + 0.5 * lvl.size[0]) % lvl.size[0] - 0.5 * lvl.size[0]
        dy = p2[1] - p1[1]
        if lvl.vertical_looping:
            dy = (dy + 0.5 * lvl.size[1]) % lvl.size[1] - 0.5 * lvl.size[1]
        
        if plajer.squish_width == 1:
            # Pursuing
            if target[1]:
                if dx < 0:
                    plajer.controls['left'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
                elif dx > 0:
                    plajer.controls['right'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
                if dy < plajer.size[1]:
                    plajer.controls['jump'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
            # Running
            else:
                if dx > 0:
                    plajer.controls['left'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
                elif dx < 0:
                    plajer.controls['right'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
                else:
                    if random.randint(0, 1):
                        plajer.controls['left'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
                    else:
                        plajer.controls['right'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
                if dy >= 0:
                    plajer.controls['jump'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
        else:
            # Respond to being squished
            if plajer.squish_width <= 0.4:
                plajer.controls['shield'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
            plajer.controls['jump'][-1] = (random.randint(0, 5) == 0) * (random.randint(0, plajer.input_noise_pile) != 0)
            if not plajer.block_on_side[0] and not plajer.block_on_side[1]:
                if random.randint(0, 1):
                    plajer.controls['left'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
                else:
                    plajer.controls['right'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
            elif not plajer.block_on_side[0]:
                plajer.controls['left'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)
            elif not plajer.block_on_side[1]:
                plajer.controls['right'][-1] = (random.randint(0, plajer.input_noise_pile) != 0)

    def get_tron_cpu_inputs(self, i):
        plajer = self.players[i]
        for control_key in plajer.controls:
            plajer.controls[control_key][-2] = plajer.controls[control_key][-1]
        ['left', 'right', 'up', 'down']




    def recount_cpu_enemies(self):
        for i, plajer in enumerate(self.players):
            if plajer.is_cpu:
                plajer.enemy_count = 0
                for ii, plaier in enumerate(self.players):
                    if i != ii:
                        if plaier.alive and not ((self.team_count > 0) and (plaier.team == plajer.team)):
                            plajer.enemy_count += 1

    def run_level(self):
        if self.mode_entrance:
            self.mode_entrance = 0
            self.su_all = 1
        
        lvl = self.levels[self.level]
        lvl.surface.fill(lvl.background_color)

        # Check if the enemy count has changed
        self.players_alive = 0
        for plajer in self.players:
            if plajer.alive:
                self.players_alive += 1
        if self.players_alive != self.lplayers_alive:
            self.recount_cpu_enemies()
        self.lplayers_alive = self.players_alive

        # Display blue sidewalls for horizontal looping
        if lvl.horizontal_looping:
            pygame.draw.rect(lvl.surface, 0x10a0ff, [[-lvl.size[0] * 0.007, 0], [lvl.size[0] * 0.01, lvl.size[1]]])
            pygame.draw.rect(lvl.surface, 0x10a0ff, [[lvl.size[0] * 0.997, 0], [lvl.size[0] * 0.01, lvl.size[1]]])
        
        # Draw unsolid blocks
        lvl.surface.blit(lvl.surface_unsolid, [0, 0])

        # Display ghosts
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if not plajer.alive:
                plajer.display(lvl, self.su_rects, self.team_colors, (self.team_count > 0))
        
        self.manage_boosts()

        for i in range(0, len(self.players)):
            self.players[i].lalive = self.players[i].alive

        for i in range(0, len(self.players)):
            if self.players[i].alive:
                self.players[i].check_squished(lvl, self.kill_width, self.players, self.death_animations)
                self.players[i].check_kill(lvl, self.players, self.kill_width, self.shield_color, i, self.death_animations)
            self.players[i].check_ground(lvl, self.players, i)

        for i in range(0, len(self.players)):
            plajer = self.players[i]
            plajer.lpos = plajer.pos[:]
            plajer.lvel = plajer.vel[:]
            plajer.lsize = plajer.size[:]
            plajer.lcolor = plajer.color
            self.hit_block = [0, 0]
            self.hit_player = [0, 0]
            
            vel_terminal = [plajer.vel_terminal[0] * (1 + bool(plajer.boosts['speed'])), plajer.vel_terminal[1]]
            vel_delta = [plajer.vel_delta[0] * (1 + bool(plajer.boosts['speed'])), plajer.vel_delta[1]]

            plajer.vel_desired = [(plajer.controls['right'][-1] - plajer.controls['left'][-1]) * vel_terminal[0], plajer.gravity]
            if not ((plajer.name.lower() == 'pac man') and (plajer.base_color == 0xffff00)):
                for ii in range(0, 2):
                    if plajer.vel[ii] < plajer.vel_desired[ii]:
                        if plajer.vel[ii] + vel_delta[ii] > plajer.vel_desired[ii]:
                            plajer.vel[ii] = plajer.vel_desired[ii]
                        else:
                            plajer.vel[ii] += vel_delta[ii]
                    elif plajer.vel[ii] > plajer.vel_desired[ii]:
                        if plajer.vel[ii] - vel_delta[ii] < plajer.vel_desired[ii]:
                            plajer.vel[ii] = plajer.vel_desired[ii]
                        else:
                            plajer.vel[ii] -= vel_delta[ii]
                    if plajer.vel[ii] > vel_terminal[ii]:
                        plajer.vel[ii] = vel_terminal[ii]
                    if plajer.vel[ii] < -vel_terminal[ii]:
                        if ii == 1:
                            if plajer.bouncing > 0:
                                plajer.bouncing -= 1
                            else:
                                plajer.vel[ii] = -vel_terminal[ii]
                        else:
                            plajer.vel[ii] = -vel_terminal[ii]
                if plajer.controls['jump'][-1]:
                    if (plajer.on_ground or plajer.on_player):
                        plajer.vel[1] = -plajer.jump_strength
                    elif not plajer.controls['jump'][-2]:
                        if plajer.boosts['jump']:
                            plajer.vel[1] = -plajer.jump_strength
                        elif (plajer.name.lower() == 'duck hunt') and (plajer.base_color == 0xff9900):
                            plajer.vel[1] = -plajer.jump_strength
                        elif (plajer.name.lower() == 'kirby') and (plajer.base_color == 0xff99cc):
                            plajer.vel[1] = -plajer.jump_strength
                
                if plajer.controls['shield'][-1] and not plajer.shield_broken:
                    plajer.vel = [0, 0]
                    plajer.color = self.shield_color
                    plajer.shield_health -= 1
                    if plajer.shield_health <= 0:
                        plajer.shield_broken = 1
                else:
                    plajer.color = plajer.base_color
                    if plajer.shield_health < plajer.shield_health_base:
                        plajer.shield_health += plajer.shield_regen
                    if plajer.shield_health >= plajer.shield_health_base:
                        plajer.shield_health = plajer.shield_health_base
                        plajer.shield_broken = 0
            else:
                new_pac_dirs = []
                if plajer.controls['left'][-1]:
                    new_pac_dirs.append([-1, 0])
                if plajer.controls['right'][-1]:
                    new_pac_dirs.append([1, 0])
                if plajer.controls['up'][-1]:
                    new_pac_dirs.append([0, -1])
                if plajer.controls['down'][-1]:
                    new_pac_dirs.append([0, 1])
                if len(new_pac_dirs):
                    plajer.pac_dir = new_pac_dirs[random.randint(0, len(new_pac_dirs) - 1)]
                if plajer.pac_dir == [-1, 0]:
                    plajer.controls['left'][-1] = 1
                elif plajer.pac_dir == [1, 0]:
                    plajer.controls['right'][-1] = 1
                plajer.vel = [plajer.pac_dir[0] * vel_terminal[0], plajer.pac_dir[1] * vel_terminal[0]]

            new_point = [plajer.pos[0] + plajer.vel[0], plajer.pos[1] + plajer.vel[1]]
            result = find_wrapped_point(new_point, plajer.size, lvl)
            plajer.pos = result[0]
            plajer.update_vel(lvl)

            for block in lvl.blocks:
                plajer.block_collision(block, lvl)
            
            # Handle the vertical collisions before player pushing
            for ii in range(0, len(self.players)):
                if i != ii:
                    plajer.player_vertical_collision(self.players[ii], lvl)

        # Player horizontal collision
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if plajer.alive:
                plajer.check_player_horizontal_collision(self.players, lvl, i)

        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if plajer.alive:
                if not (plajer.controls['shield'][-1] and not plajer.shield_broken):
                    plajer.pos[0] += 0.5 * sum(plajer.vel_external)
                plajer.propogate_push(self.players)
        
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if plajer.alive:
                plajer.save_old_rect()
                plajer.squish(lvl, self.players, self.squish_delta)
                plajer.save_new_rect()
                plajer.load_old_rect()
            else:
                plajer.expand(lvl, self.squish_delta)
        
        # Update projectiles
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if plajer.alive:
                plajer.load_new_rect()
            if plajer.vel[0]:
                plajer.facing = sign(plajer.vel[0])
            if (plajer.name.lower() == 'link') and (plajer.base_color == 0x008800):
                # Tick player's arrow timer
                if plajer.arrow_counter > 0:
                    plajer.arrow_counter += -1
                # Spawn new arrow
                if plajer.controls['ability'][-1]:
                    if plajer.spawn_arrow(lvl, self.img_arrow):
                            self.su_rects.append([plajer.arrows[-1].pos, plajer.arrows[-1].size])
                # Move existing arrows
                kill_arrows = []
                for ii in range(0, len(plajer.arrows)):
                    arrov = plajer.arrows[ii]
                    arrov_lpos = arrov.pos[:]
                    arrov.vel[1] += arrov.gravity
                    arrov.pos[0] += arrov.vel[0]
                    arrov.pos[1] += arrov.vel[1]
                    if lvl.horizontal_looping:
                        arrov.pos[0] %= lvl.size[0]
                    if lvl.vertical_looping:
                        arrov.pos[1] %= lvl.size[1]
                    if arrov.vel != [0, 0]:
                        for block in lvl.blocks:
                            if block.solid:
                                overlap = rect_overlap(block.pos, block.size, [0, 0], arrov.pos, arrov.size, lwl = lvl)
                                if magnitude(overlap) >= plajer.penetration_depth:
                                    arrov.gravity = 0
                                    arrov.vel = [0, 0]
                                    self.su_rects.append([arrov.pos, arrov.size])
                    if (arrov.vel != [0, 0]) and plajer.alive:
                        for iii in range(0, len(self.players)):
                            if i != iii:
                                plaier = self.players[iii]
                                if plaier.alive:
                                    overlap = rect_overlap(plaier.pos, plaier.size, [0, 0], arrov.pos, arrov.size, lwl = lvl)
                                    if magnitude(overlap) >= plajer.penetration_depth:
                                        plaier.ability_death(plajer, self.shield_color, self.death_animations, lvl)
                    else:
                        if arrov.life <= 0:
                            kill_arrows.append(ii)
                            self.su_rects.append([arrov_lpos, arrov.size])
                        else:
                            arrov.life += -1
                    if arrov.pos != arrov_lpos:
                        self.su_rects.append([arrov_lpos, arrov.size])
                        self.su_rects.append([arrov.pos, arrov.size])
                    # Display arrows
                    if arrov.life > 0:
                        lvl.surface.blit(arrov.image, arrov.pos)
                kill_arrows.sort(reverse = 1)
                for i in kill_arrows:
                    plajer.arrows.pop(i)
            elif ((plajer.name.lower() == 'ness') and (plajer.base_color == 0x888800)) or ((plajer.name.lower() == 'bowser') and (plajer.base_color == 0xff9900)):
                # Tick player's fire timer
                if plajer.fire_counter > 0:
                    plajer.fire_counter += -1
                # Spawn new fire
                if plajer.controls['ability'][-1]:
                    if plajer.spawn_fire(lvl, self.img_fire):
                        self.su_rects.append([plajer.fires[-1].pos, plajer.fires[-1].size])
                # Move existing fires
                kill_fires = []
                for ii in range(0, len(plajer.fires)):
                    fyre = plajer.fires[ii]
                    fyre_lpos = fyre.pos[:]
                    fyre.pos[0] += fyre.vel[0]
                    fyre.pos[1] += fyre.vel[1]
                    if lvl.horizontal_looping:
                        fyre.pos[0] %= lvl.size[0]
                    if lvl.vertical_looping:
                        fyre.pos[1] %= lvl.size[1]
                    if plajer.alive:
                        for iii in range(0, len(self.players)):
                            if i != iii:
                                plaier = self.players[iii]
                                if plaier.alive:
                                    overlap = rect_overlap(plaier.pos, plaier.size, [0, 0], fyre.pos, fyre.size, lwl = lvl)
                                    if magnitude(overlap) >= plajer.penetration_depth:
                                        plaier.ability_death(plajer, self.shield_color, self.death_animations, lvl)
                    for block in lvl.blocks:
                        if block.solid:
                            overlap = rect_overlap(block.pos, block.size, [0, 0], fyre.pos, fyre.size, lwl = lvl)
                            if magnitude(overlap) >= plajer.penetration_depth:
                                fyre.vel = [0, 0]
                    if fyre.life <= 0:
                        kill_fires.append(ii)
                        self.su_rects.append([fyre_lpos, fyre.size])
                    else:
                        fyre.life += -1
                    # Display fires
                    if fyre.life > 0:
                        lvl.surface.blit(fyre.image, fyre.pos)
                    if fyre.pos != fyre_lpos:
                        self.su_rects.append([fyre_lpos, fyre.size])
                        self.su_rects.append([fyre.pos, fyre.size])
                kill_fires.sort(reverse = 1)
                for i in kill_fires:
                    plajer.fires.pop(i)
            elif (plajer.name.lower() == 'pikachu') and (plajer.base_color == 0xffff00):
                # Tick player's zap timer
                if plajer.zap_counter > 0:
                    plajer.zap_counter += -1
                # Spawn new zap
                if plajer.controls['ability'][-1]:
                    if plajer.spawn_zap(self.imgs_zap, self.colorkey):
                        self.su_rects.append([plajer.zaps[-1].pos, plajer.zaps[-1].size])
                # Move existing zaps
                kill_zaps = []
                for ii in range(0, len(plajer.zaps)):
                    zap = plajer.zaps[ii]
                    if (zap.life > 0):
                        zap.life += -1
                        zap.lpos = zap.pos[:]
                        if zap.facing > 0:
                            zap.pos = [plajer.pos[0] + plajer.size[0], plajer.pos[1] + 0.5 * plajer.size[1] - 0.5 * zap.size[1]]
                        else:
                            zap.pos = [plajer.pos[0] - zap.size[0], plajer.pos[1] + 0.5 * plajer.size[1] - 0.5 * zap.size[1]]
                        if plajer.alive:
                            for iii in range(0, len(self.players)):
                                if i != iii:
                                    plaier = self.players[iii]
                                    if plaier.alive:
                                        overlap = rect_overlap(plaier.pos, plaier.size, [0, 0], zap.pos, zap.size, lwl = lvl)
                                        if magnitude(overlap) >= plajer.penetration_depth:
                                            plaier.ability_death(plajer, self.shield_color, self.death_animations, lvl)
                    else:
                        kill_zaps.append(ii)
                kill_zaps.sort(reverse = 1)
                for i in kill_zaps:
                    zap = plajer.zaps.pop(i)
                    self.su_rects.append([zap.lpos, zap.size])
                    self.su_rects.append([zap.pos, zap.size])

        # Display solid blocks
        lvl.surface.blit(lvl.surface_solid, [0, 0])

        # Display red line for not vertical looping, kill players below it, and also put a roof
        if not lvl.vertical_looping:
            pygame.draw.rect(lvl.surface, 0xff0000, [[0, lvl.size[1] * 0.996], [lvl.size[0], lvl.size[1] * 0.01]])
            for plajer in self.players:
                if plajer.alive and (plajer.pos[1] >= lvl.size[1]):
                    plajer.alive = 0
                if plajer.pos[1] >= lvl.size[1] + 6 * plajer.base_size[1]:
                    plajer.vel[1] = -1.67 * lvl.player_gravity * lvl.player_jump_strength / plajer.jump_strength
                    plajer.bouncing = 30
                if plajer.pos[1] < -plajer.base_size[1]:
                    plajer.pos[1] = -plajer.base_size[1]
                    if plajer.vel[1] < 0:
                        plajer.vel[1] = 0

        self.display_boosts()

        # Display players
        player_cnt = 0
        self.winner_index = 0
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if plajer.alive:
                player_cnt += 1
                self.winner_index = i
                plajer.display(lvl, self.su_rects, self.team_colors, (self.team_count > 0))
            elif plajer.lalive:
                plajer.display(lvl, self.su_rects, self.team_colors, (self.team_count > 0))
                plajer.append_su_rects(lvl, self.su_rects)
        
        self.kill_animations()

        self.kill_anis = []
        for i in range(0, len(self.death_animations)):
            ani = self.death_animations[i]
            for rect in ani.get_rects():
                pygame.draw.rect(lvl.surface, ani.color, rect)
                self.su_rects.append(rect)
            for rect in ani.lrects:
                self.su_rects.append(rect)
            if ani.life <= 0:
                self.kill_anis.append(i)

        # Display zaps
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if (plajer.name.lower() == 'pikachu') and (plajer.base_color == 0xffff00):
                for ii in range(0, len(plajer.zaps)):
                    zap = plajer.zaps[ii]
                    lvl.surface.blit(zap.get_image(), zap.pos)
                    self.su_rects.append([zap.lpos, zap.size])
                    self.su_rects.append([zap.pos, zap.size])
        
        # Detect victory
        if self.team_count and (len(self.death_animations) == 0):
            self.winning_team = self.detect_team_win()
            if self.winning_team != None:
                for plajer in self.players:
                    if plajer.team == self.winning_team:
                        plajer.wins += 1
                self.do_actions([['goto', 'end_game']])
        elif (player_cnt <= 1) and (len(self.death_animations) == 0):
            self.players[self.winner_index].wins += 1
            # [Redact] this
            #self.save_cpu_weights()
            #if self.file_val >= 9999:
            self.do_actions([['goto', 'end_game']])
            #else:
            #    # Don't Redact this
            #    self.do_actions([['play_level', 'random']])
        
        self.play_level_sounds()

        self.surface.blit(pygame.transform.scale(lvl.surface, self.surface_size), [0, 0])

    def play_level_sounds(self):
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if plajer.lalive and not plajer.alive:
                self.sound.sounds['squish'].play()
            if (plajer.air_time <= 0) and (plajer.lair_time > 50):
                self.sound.sounds['land'].play()
            if (plajer.air_time == 45) and (plajer.vel[1] == plajer.vel_terminal[1]):
                self.sound.sounds['fall'].play()

    def initialize_boosts(self):
        self.boost_spawn_spots = 4
        self.boost_fall_speed = 0.02
        self.boost_types = {'invincible' : 500,
                            'jump'       : 300,
                            'kill'       : 300,
                            'phase'      : 500,
                            'speed'      : 300}

    def reset_boosts(self):
        self.boost_counter = 0
        # Each entry should be [[int x, int y], str boost_name, int falling]
        self.boosts = []
        player_size = self.levels[self.level].player_size
        boost_size = 0.75 * 0.5 * (player_size[0] + player_size[1])
        self.boost_size = [boost_size, boost_size]
        self.img_boosts_scaled = {}
        for key in self.img_boosts:
            self.img_boosts_scaled[key] = pygame.transform.scale(self.img_boosts[key], self.boost_size)

    def manage_boosts(self):
        if self.boosts_on:
            lvl = self.levels[self.level]
            target_radius = 0.5 * ((lvl.size[0] ** 2 + lvl.size[1] ** 2) ** 0.5)

            # Track active boosts
            for plajer in self.players:
                for key in plajer.boosts:
                    if plajer.boosts[key] > 0:
                        plajer.boosts[key] += -1

            # Spawn new boosts
            if self.boost_counter >= self.boost_periodicity:
                if random.randint(0, self.boost_draw_pile) == 0:
                    possible_poses = []
                    # Ensure no block or player overlap
                    for i in range(0, self.boost_spawn_spots):
                        possible_poses.append([random.randint(0, lvl.size[0] - 1), random.randint(0, lvl.size[1] - 1)])
                    kill_possible_poses = []
                    for i in range(0, len(possible_poses)):
                        pos = possible_poses[i]
                        rect_pos = [pos[0] - 0.5 * self.boost_size[0], pos[1] - 0.5 * self.boost_size[1]]
                        for block in lvl.blocks:
                            if block.solid:
                                if rect_overlap(rect_pos, self.boost_size, [0, 0], block.pos, block.size, lwl = lvl) != [0, 0]:
                                    if not kill_possible_poses.count(i):
                                        kill_possible_poses.append(i)
                        for plajer in self.players:
                            if plajer.alive:
                                if rect_overlap(rect_pos, self.boost_size, [0, 0], plajer.pos, plajer.size, lwl = lvl) != [0, 0]:
                                    if not kill_possible_poses.count(i):
                                        kill_possible_poses.append(i)
                    kill_possible_poses.sort(reverse = 1)
                    for i in kill_possible_poses:
                        possible_poses.pop(i)

                    # Pick the position that is closest to the target radius for each player
                    if len(possible_poses) and len(self.players):
                        distances = []
                        for i in range(0, len(possible_poses)):
                            pos = possible_poses[i]
                            sub_distances = []
                            for plajer in self.players:
                                sub_distances.append(abs(target_radius - distance(pos, plajer.center())))
                            distances.append(max(sub_distances))
                        pos = possible_poses[distances.index(min(distances))]
                        boost_type = [*self.boost_types][random.randint(0, len(self.boost_types) - 1)]
                        self.boosts.append([pos, boost_type, 1])
                    self.boost_counter = 0
            else:
                self.boost_counter += 1

            # Make boosts fall appropriately
            kill_boosts = []
            for i in range(0, len(self.boosts)):
                boost = self.boosts[i]
                if boost[2]:
                    rect_pos = [boost[0][0] - 0.5 * self.boost_size[0], boost[0][1] - 0.5 * self.boost_size[1]]
                    increase = lvl.player_gravity * self.boost_fall_speed
                    self.su_rects.append([[rect_pos[0], rect_pos[1] - 0.1 * increase], [self.boost_size[0], self.boost_size[1] + 1.2 * increase]])
                    rect_pos[1] += increase
                    for block in lvl.blocks:
                        if block.solid:
                            overlap = rect_overlap(rect_pos, self.boost_size, [0, 0], block.pos, block.size)
                            if overlap != [0, 0]:
                                boost[0][1] += increase - abs(overlap[1])
                                boost[2] = 0
                                break
                    boost[0][1] += increase
                    if boost[0][1] - 0.5 * self.boost_size[1] > lvl.size[1]:
                        kill_boosts.append(i)
            kill_boosts.sort(reverse = 1)
            for i in kill_boosts:
                boost = self.boosts.pop(i)
                rect_pos = [boost[0][0] - 0.5 * self.boost_size[0], boost[0][1] - 0.5 * self.boost_size[1]]
                self.su_rects.append([[rect_pos[0], rect_pos[1] - 0.1 * self.boost_size[1]], [self.boost_size[0], self.boost_size[1] + 0.2 * self.boost_size[1]]])

            # Give player boost on collision
            kill_boosts = []
            for i in range(0, len(self.boosts)):
                boost = self.boosts[i]
                rect_pos = [boost[0][0] - 0.5 * self.boost_size[0], boost[0][1] - 0.5 * self.boost_size[1]]
                farthest_radius = 0
                index = None
                for ii in range(0, len(self.players)):
                    plajer = self.players[ii]
                    if plajer.alive:
                        if rect_overlap(rect_pos, self.boost_size, [0, 0], plajer.pos, plajer.size, lwl = lvl) != [0, 0]:
                            dist = abs(target_radius - distance(rect_pos, plajer.center()))
                            if dist > farthest_radius:
                                farthest_radius = dist
                                index = ii
                if index != None:
                    self.players[index].boosts[self.boosts[i][1]] = self.boost_types[self.boosts[i][1]]
                    kill_boosts.append(i)
            kill_boosts.sort(reverse = 1)
            for i in kill_boosts:
                boost = self.boosts.pop(i)
                rect_pos = [boost[0][0] - 0.5 * self.boost_size[0], boost[0][1] - 0.5 * self.boost_size[1]]
                self.su_rects.append([[rect_pos[0], rect_pos[1] - 0.1 * self.boost_size[1]], [self.boost_size[0], self.boost_size[1] + 0.2 * self.boost_size[1]]])

    def display_boosts(self):
        if self.boosts_on:
            for boost in self.boosts:
                pos = [boost[0][0] - 0.5 * self.boost_size[0], boost[0][1] - 0.5 * self.boost_size[1]]
                self.levels[self.level].surface.blit(self.img_boosts_scaled[boost[1]], pos)

    def kill_animations(self):
        lem = len(self.kill_anis)
        for i in range(0, lem):
            h = lem - i - 1
            ani = self.death_animations.pop(h)
            for rect in ani.rects:
                self.su_rects.append(rect)

    def do_actions(self, actions, index = -1):
        for action in actions:
            if action[0] == 'quit':
                self.running = 0
            elif action[0] == 'goto':
                self.mode = 'page'
                self.next_page = action[1]
                self.menu_controls['page_entrance'] = 1
            elif action[0] == 'save_settings':
                self.save_settings()
            elif action[0] == 'select_level':
                if action[1] == 'from_list':
                    if len(self.levels) > index:
                        self.level = [*self.levels][index]
            elif action[0] == 'load_levels':
                self.load_levels()
            elif action[0] == 'save_level':
                if (self.level != self.levels[self.level].name) and (os.listdir(self.level_directory).count(self.level + '.txt')):
                    os.remove(os.path.join(self.level_directory, self.level + '.txt'))
                    self.levels[self.level].export_level_file()
                    name = self.levels[self.level].name
                    self.load_levels()
                    self.level = name
                else:
                    self.levels[self.level].export_level_file()
            elif action[0] == 'play_level':
                if len(self.players) <= 0:
                    self.do_actions([['play_scythe']])
                elif len(self.players) == 1:
                    self.do_actions([['play_snake']])
                else:
                    if len(action) > 1:
                        if action[1] == 'from_list':
                            if len(self.levels) > index:
                                self.level = [*self.levels][index]
                        elif action[1] == 'random':
                            if len(self.levels) > 0:
                                i = random.Random().randint(0, len(self.levels) - 1)
                                self.level = [*self.levels][i]
                    if self.level.lower() == 'tron':
                        self.do_actions([['play_tron']])
                    else:
                        for key in self.sound.music:
                            self.sound.music[key].stop()
                        self.mode = 'squish'
                        self.initialize_level()
            elif action[0] == 'set_level':
                if action[1] == 'from_list':
                    if len(self.levels) > index:
                        self.level = [*self.levels][index]
                elif action[1] == 'random':
                    if len(self.levels) > 0:
                        i = random.Random().randint(0, len(self.levels) - 1)
                        self.level = [*self.levels][i]
            elif action[0] == 'resume_level':
                self.mode = 'squish'
                pygame.mouse.set_visible(0)
                self.mode_entrance = 1
            elif action[0] == 'conditional':
                if action[1] == 'teams_on':
                    if self.team_count > 0:
                        self.do_actions([action[2:]])
                elif action[1] == 'teams_off':
                    if self.team_count == 0:
                        self.do_actions([action[2:]])
            elif action[0] == 'check_teams':
                self.check_teams()
            elif action[0] == 'player_choose_team':
                self.player_choose_team()
            elif action[0] == 'distribute_players':
                self.distribute_players()
            elif action[0] == 'reset_editor':
                self.reset_editor_tools()
            elif action[0] == 'edit_level':
                self.mode = 'editor'
                self.soft_reset_editor_tools()
                self.mode_entrance = 1
            elif action[0] == 'editor_display_level':
                self.mode_entrance = 1
                self.su_all = 1
                self.editor_display_level()
                self.surface_screenshot = self.surface.copy()
            elif action[0] == 'editor_pull_forward':
                self.edit_index_shifted += 1
                if self.edit_index_shifted >= len(self.levels[self.level].blocks):
                    self.edit_index_shifted = len(self.levels[self.level].blocks) - 1
            elif action[0] == 'editor_push_back':
                self.edit_index_shifted += -1
                if self.edit_index_shifted < 0:
                    self.edit_index_shifted = 0
            elif action[0] == 'update_edited_block':
                self.levels[self.level].blocks[self.edit_index] = self.edited_block
                self.levels[self.level].blocks.insert(self.edit_index_shifted, self.levels[self.level].blocks.pop(self.edit_index))
            elif action[0] == 'update_edited_player':
                self.levels[self.level].player_poses[self.edit_index] = self.edited_player_pos
            elif action[0] == 'update_edited_background':
                self.levels[self.level].background_color = self.edited_background
            elif action[0] == 'editor_duplicate_horizontally':
                self.levels[self.level].duplicate(0)
            elif action[0] == 'editor_duplicate_vertically':
                self.levels[self.level].duplicate(1)
            elif action[0] == 'editor_duplicate_undo':
                self.levels[self.level].undo()
            elif action[0] == 'render_thumbnail':
                self.levels[self.level].render_thumbnail()
            elif action[0] == 'update_controllers': # [Redact] this, it isn't being used
                self.reset_joysticks()
            elif action[0] == 'save_players':
                self.save_player_data()
            elif action[0] == 'map_controls':
                self.map_controls()
            elif action[0] == 'reset_mapping':
                self.reset_mapping()
            elif action[0] == 'new':
                if action[1] == 'level':
                    key = 'Level ' + str(len(self.levels) + 1)
                    keys = [*self.levels]
                    file = open(os.path.join(self.cwd, 'defualt_level.txt'), encoding = 'utf-8')
                    default_level = file.readlines()
                    file.close()
                    while 1:
                        has_key = 0
                        for cey in keys:
                            if cey.lower() == key.lower():
                                has_key = 1
                                break
                        if not has_key:
                            self.levels[key] = level(default_level, key)
                            break
                        key = key + '-'
                    self.level = key
                elif action[1] == 'player':
                    self.players.append(player(self.players))
            elif action[0] == 'set':
                if action[1] == 'level':
                    if action[2] == 'background_color':
                        self.levels[self.level].background_color = int(action[3], 16)
                elif action[1] == 'game':
                    if action[2] == 'teaming':
                        self.teaming = (action[3].lower() == 'true') or (action[3] == '1')
                elif action[1] == 'player':
                    if action[2] == 'base_color':
                        self.players[-1].base_color = int(action[3], 16)
                elif action[1] == 'editor':
                    if action[2] == 'tool':
                        self.tool = action[3]
                    elif action[2] == 'block_color':
                        self.editor_block_color = int(action[3], 16)
                    elif action[2] == 'block':
                        if action[3] == 'color':
                            self.edited_block.color = int(action[4], 16)
                    elif action[2] == 'background':
                        if action[3] == 'color':
                            self.edited_background = int(action[4], 16)
            elif action[0] == 'input':
                # HERE 1
                if action[1] == 'level':
                    if action[2] == 'name':
                        self.text_input = self.levels[self.level].name
                        self.valid_inputs = self.valid_name_inputs
                    elif action[2] == 'width':
                        self.text_input = str(self.levels[self.level].size[0])
                        self.valid_inputs = self.valid_int_inputs
                    elif action[2] == 'height':
                        self.text_input = str(self.levels[self.level].size[1])
                        self.valid_inputs = self.valid_int_inputs
                    elif action[2] == 'background_color':
                        self.text_input = hex(self.levels[self.level].background_color)[2:].rjust(6, '0')
                        self.valid_inputs = self.valid_hex_inputs
                    elif action[2] == 'side_wall_depth':
                        self.text_input = str(self.levels[self.level].side_wall_depth)
                        self.valid_inputs = self.valid_float_inputs
                elif action[1] == 'player':
                    if action[2] == 'name':
                        self.text_input = self.players[-1].name
                        self.valid_inputs = self.valid_name_inputs
                    elif action[2] == 'base_color':
                        self.text_input = hex(self.players[-1].base_color)[2:].rjust(6, '0')
                        self.valid_inputs = self.valid_hex_inputs
                    elif action[2] == 'width':
                        self.text_input = str(self.levels[self.level].player_size[0])
                        self.valid_inputs = self.valid_float_inputs
                    elif action[2] == 'height':
                        self.text_input = str(self.levels[self.level].player_size[1])
                        self.valid_inputs = self.valid_float_inputs
                    elif action[2] == 'gravity':
                        self.text_input = str(self.levels[self.level].player_gravity)
                        self.valid_inputs = self.valid_float_inputs
                    elif action[2] == 'jump_strength':
                        self.text_input = str(self.levels[self.level].player_jump_strength)
                        self.valid_inputs = self.valid_float_inputs
                    elif action[2] == 'y_vel_terminal':
                        self.text_input = str(self.levels[self.level].player_vel_terminal[1])
                        self.valid_inputs = self.valid_float_inputs
                    elif action[2] == 'x_vel_terminal':
                        self.text_input = str(self.levels[self.level].player_vel_terminal[0])
                        self.valid_inputs = self.valid_float_inputs
                    elif action[2] == 'y_vel_delta':
                        self.text_input = str(self.levels[self.level].player_vel_delta[1])
                        self.valid_inputs = self.valid_float_inputs
                    elif action[2] == 'x_vel_delta':
                        self.text_input = str(self.levels[self.level].player_vel_delta[0])
                        self.valid_inputs = self.valid_float_inputs
                    elif action[2] == 'shield_health':
                        self.text_input = str(self.levels[self.level].player_shield_health_base)
                        self.valid_inputs = self.valid_float_inputs
                    elif action[2] == 'shield_regen':
                        self.text_input = str(self.levels[self.level].player_shield_regen)
                        self.valid_inputs = self.valid_float_inputs
                elif action[1] == 'editor':
                    if action[2] == 'block_color':
                        self.text_input = hex(self.editor_block_color)[2:].rjust(6, '0')
                        self.valid_inputs = self.valid_hex_inputs
                    elif action[2] == 'block':
                        if action[3] == 'color':
                            self.text_input = hex(self.edited_block.color)[2:].rjust(6, '0')
                            self.valid_inputs = self.valid_hex_inputs
                        elif action[3] == 'x_pos':
                            self.text_input = str(self.edited_block.pos[0])
                            self.valid_inputs = self.valid_int_inputs
                        elif action[3] == 'y_pos':
                            self.text_input = str(self.edited_block.pos[1])
                            self.valid_inputs = self.valid_int_inputs
                        elif action[3] == 'x_size':
                            self.text_input = str(self.edited_block.size[0])
                            self.valid_inputs = self.valid_int_inputs
                        elif action[3] == 'y_size':
                            self.text_input = str(self.edited_block.size[1])
                            self.valid_inputs = self.valid_int_inputs
                    elif action[2] == 'player':
                        if action[3] == 'x_pos':
                            self.text_input = str(self.edited_player_pos[0])
                            self.valid_inputs = self.valid_int_inputs
                        elif action[3] == 'y_pos':
                            self.text_input = str(self.edited_player_pos[1])
                            self.valid_inputs = self.valid_int_inputs
                    elif action[2] == 'background':
                        if action[3] == 'color':
                            self.text_input = hex(self.edited_background)[2:].rjust(6, '0')
                            self.valid_inputs = self.valid_hex_inputs
                        
                self.text_last_input = self.text_input
                self.text_input_action = action
                pygame.key.set_repeat(500, 100)
                if self.valid_int_inputs.count(action[-1][-1]):
                    self.text_input_limit = int(action[-1])
                else:
                    self.text_input_limit = -1
            elif action[0] == 'toggle':
                if action[1] == 'level':
                    if action[2] == 'vertical_looping':
                        self.levels[self.level].vertical_looping = not self.levels[self.level].vertical_looping
                    elif action[2] == 'horizontal_looping':
                        self.levels[self.level].horizontal_looping = not self.levels[self.level].horizontal_looping
                elif action[1] == 'player':
                    if action[2] == 'is_cpu':
                        self.players[-1].is_cpu = not self.players[-1].is_cpu
                elif action[1] == 'game':
                    if action[2] == 'fullscreen':
                        self.toggle_fullscreen()
                    elif action[2] == 'resolution':
                        self.toggle_resolution()
                    elif action[2] == 'show_fps':
                        self.show_fps = not self.show_fps
                        self.su_all = 1
                    elif action[2] == 'boosts_on':
                        self.boosts_on = not self.boosts_on
                    elif action[2] == 'team_count':
                        self.team_count = (self.team_count + 1) % (self.max_teams + 1)
                        if self.team_count == 1:
                            self.team_count = 2
                elif action[1] == 'editor':
                    if action[2] == 'mirroring':
                        self.editor_mirroring = not self.editor_mirroring
                    elif action[2] == 'block_solid':
                        self.editor_block_solid = not self.editor_block_solid
                    elif action[2] == 'block':
                        if action[3] == 'solid':
                            self.edited_block.solid = not self.edited_block.solid
            elif action[0] == 'copy':
                if action[1] == 'level':
                    if action[2] == 'from_list':
                        keys = [*self.levels]
                        key = keys[index]
                        new_key = key
                        while 1:
                            new_key = new_key + '-'
                            has_key = 0
                            for cey in keys:
                                if cey.lower() == new_key.lower():
                                    has_key = 1
                                    break
                            if not has_key:
                                self.levels[new_key] = level(self.levels[key].file, new_key)
                                break
                        self.levels[new_key].export_level_file()
            elif action[0] == 'delete':
                if action[1] == 'level':
                    if (len(action) >= 3) and (action[2] == 'from_list'):
                        key = [*self.levels][index]
                        os.remove(os.path.join(self.level_directory, key + '.txt'))
                    else:
                        key = self.level
                        os.remove(os.path.join(self.level_directory, key + '.txt'))
                elif action[1] == 'player':
                    if (len(action) >= 3) and (action[2] == 'from_list'):
                        if len(self.players) > index:
                            self.players.pop(index)
                    else:
                        self.players.pop()
                elif action[1] == 'all_players':
                    self.players = []
            elif action[0] == 'find_list_buttons':
                self.find_list_buttons()
            elif action[0] == 'draw_alpha':
                self.draw_alpha(int(action[1], 16), int(action[2]))
            elif action[0] == 'play_snake':
                self.mode = 'snake'
                self.snake_game.restart(self.surface_size, self.players[0].base_color, self.players[0].name, self.tick_speed)
                self.mode_entrance = 1
            elif action[0] == 'play_scythe':
                self.mode = 'scythe'
                self.scythe_game.restart(self.surface_size)
                self.mode_entrance = 1
            elif action[0] == 'play_tron':
                self.mode = 'tron'
                self.tron_game.restart(self.players, self.team_count, self.team_colors)
                self.mode_entrance = 1
            elif action[0] == 'resume_tron':
                self.mode = 'tron'
                self.mode_entrance = 1
            elif action[0] == 'stop_music':
                for key in self.sound.music:
                    self.sound.music[key].stop()

    def apply_text_input(self, text):
        if self.text_input_action != -1:
            # HERE 2
            if self.text_input_action[1] == 'level':
                if self.text_input_action[2] == 'name':
                    key = text
                    keys = [*self.levels]
                    while 1:
                        has_key = 0
                        for cey in keys:
                            if cey.lower() == key.lower():
                                if key.lower() != self.level.lower():
                                    has_key = 1
                                    break
                        if not has_key:
                            break
                        key = key + '-'
                    self.levels[self.level].name = key
                elif self.text_input_action[2] == 'width':
                    if text == '':
                        self.levels[self.level].size[0] = 1
                    else:
                        self.levels[self.level].size[0] = int(text)
                    self.levels[self.level].rescale()
                elif self.text_input_action[2] == 'height':
                    if text == '':
                        self.levels[self.level].size[1] = 1
                    else:
                        self.levels[self.level].size[1] = int(text)
                    self.levels[self.level].rescale()
                elif self.text_input_action[2] == 'background_color':
                    if text:
                        self.levels[self.level].background_color = int(text.ljust(6, '0'), 16)
                    else:
                        self.levels[self.level].background_color = 0xbbbbbb
                elif self.text_input_action[2] == 'side_wall_depth':
                    if text == '':
                        self.levels[self.level].side_wall_depth = 0.0
                    else:
                        side_wall_depth = float(text)
                        if side_wall_depth > 100:
                            side_wall_depth = 100.0
                        self.levels[self.level].side_wall_depth = side_wall_depth
            elif self.text_input_action[1] == 'player':
                if self.text_input_action[2] == 'name':
                    self.players[-1].name = text
                elif self.text_input_action[2] == 'base_color':
                    if text:
                        self.players[-1].base_color = int(text.ljust(6, '0'), 16)
                    else:
                        self.players[-1].base_color = 0xbbbbbb
                elif self.text_input_action[2] == 'width':
                    if text == '':
                        self.levels[self.level].player_size[0] = 0.0
                    else:
                        self.levels[self.level].player_size[0] = float(text)
                elif self.text_input_action[2] == 'height':
                    if text == '':
                        self.levels[self.level].player_size[1] = 0.0
                    else:
                        self.levels[self.level].player_size[1] = float(text)
                elif self.text_input_action[2] == 'gravity':
                    if text == '':
                        self.levels[self.level].player_gravity = 0.0
                    else:
                        self.levels[self.level].player_gravity = float(text)
                elif self.text_input_action[2] == 'jump_strength':
                    if text == '':
                        self.levels[self.level].player_jump_strength = 0.0
                    else:
                        self.levels[self.level].player_jump_strength = float(text)
                elif self.text_input_action[2] == 'y_vel_terminal':
                    if text == '':
                        self.levels[self.level].player_vel_terminal[1] = 0.0
                    else:
                        self.levels[self.level].player_vel_terminal[1] = float(text)
                elif self.text_input_action[2] == 'x_vel_terminal':
                    if text == '':
                        self.levels[self.level].player_vel_terminal[0] = 0.0
                    else:
                        self.levels[self.level].player_vel_terminal[0] = float(text)
                elif self.text_input_action[2] == 'y_vel_delta':
                    if text == '':
                        self.levels[self.level].player_vel_delta[1] = 0.0
                    else:
                        self.levels[self.level].player_vel_delta[1] = float(text)
                elif self.text_input_action[2] == 'x_vel_delta':
                    if text == '':
                        self.levels[self.level].player_vel_delta[0] = 0.0
                    else:
                        self.levels[self.level].player_vel_delta[0] = float(text)
                elif self.text_input_action[2] == 'shield_health':
                    if text == '':
                        self.levels[self.level].player_shield_health_base = 0.0
                    else:
                        self.levels[self.level].player_shield_health_base = float(text)
                elif self.text_input_action[2] == 'shield_regen':
                    if text == '':
                        self.levels[self.level].player_shield_regen = 0.0
                    else:
                        self.levels[self.level].player_shield_regen = float(text)
            elif self.text_input_action[1] == 'editor':
                if self.text_input_action[2] == 'block_color':
                    if text:
                        self.editor_block_color = int(text.ljust(6, '0'), 16)
                    else:
                        self.editor_block_color = 0xbbbbbb
                elif self.text_input_action[2] == 'block':
                    if self.text_input_action[3] == 'color':
                        if text:
                            self.edited_block.color = int(text.ljust(6, '0'), 16)
                        else:
                            self.edited_block.color = 0x000000
                    elif self.text_input_action[3] == 'x_pos':
                        if text:
                            self.edited_block.pos[0] = int(text)
                        else:
                            self.edited_block.pos[0] = 0
                    elif self.text_input_action[3] == 'y_pos':
                        if text:
                            self.edited_block.pos[1] = int(text)
                        else:
                            self.edited_block.pos[1] = 0
                    elif self.text_input_action[3] == 'x_size':
                        if text:
                            self.edited_block.size[0] = int(text)
                        else:
                            self.edited_block.size[0] = 0
                    elif self.text_input_action[3] == 'y_size':
                        if text:
                            self.edited_block.size[1] = int(text)
                        else:
                            self.edited_block.size[1] = 0
                elif self.text_input_action[2] == 'player':
                    if self.text_input_action[3] == 'x_pos':
                        if text:
                            self.edited_player_pos[0] = int(text)
                        else:
                            self.edited_player_pos[0] = 0
                    elif self.text_input_action[3] == 'y_pos':
                        if text:
                            self.edited_player_pos[1] = int(text)
                        else:
                            self.edited_player_pos[1] = 0
                elif self.text_input_action[2] == 'background':
                    if self.text_input_action[3] == 'color':
                        if text:
                            self.edited_background = int(text.ljust(6, '0'), 16)
                        else:
                            self.edited_background = 0xbbbbbb

    def load_player_data(self):
        file = open(os.path.join(self.cwd, 'player_data.txt'), encoding = 'utf-8')
        self.players = []
        for line in file:
            no_spaces_line = line.replace(' ', '')
            no_comment_line = no_spaces_line.split('#')[0]
            no_return_line = no_comment_line.replace('\n', '')
            split_line = no_return_line.split('=')
            properky = split_line[0]
            value = split_line[-1]
            if properky == 'player':
                self.players.append(player(self.players))
            elif properky == 'name':
                self.players[-1].name = line.split('=')[-1][1:-1]
            elif properky == 'base_color':
                self.players[-1].base_color = int(value, 16)
            elif properky == 'kills':
                self.players[-1].kills = int(value)
            elif properky == 'wins':
                self.players[-1].wins = int(value)
            elif properky == 'team':
                self.players[-1].team = int(value)
            elif properky == 'is_cpu':
                self.players[-1].is_cpu = (value.lower() == 'true') or (value == '1')
            else:
                for control in self.players[-1].controls:
                    if properky == control:
                        control_stuff = value.replace('[', '').replace(']', '').split(',')
                        if control_stuff[0] == '-1':
                            self.players[-1].controls[control] = [int(control_stuff[0]), int(control_stuff[1]), 0, 0]
                        else:
                            if control_stuff[1].replace("'", '') == 'hat':
                                self.players[-1].controls[control] = [int(control_stuff[0]), control_stuff[1].replace("'", ''), int(control_stuff[2]), (int(control_stuff[3].replace('(', '')), int(control_stuff[4].replace(')', ''))), 0, 0]
                            else:
                                self.players[-1].controls[control] = [int(control_stuff[0]), control_stuff[1].replace("'", ''), int(control_stuff[2]), int(control_stuff[3]), 0, 0]
                        break
        file.close()

    def save_player_data(self):
        file = open(os.path.join(self.cwd, 'player_data.txt'), mode = 'w', encoding = 'utf-8')
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if i != 0:
                file.write('\n\n')
            file.write('player\n')
            file.write('    name = ' + plajer.name + '\n')
            file.write('    base_color = 0x' + hex(plajer.base_color)[2:].rjust(6, '0') + '\n')
            file.write('    kills = ' + str(plajer.kills) + '\n')
            file.write('    wins = ' + str(plajer.wins) + '\n')
            file.write('    team = ' + str(plajer.team) + '\n')
            file.write('    is_cpu = ' + 'true' * (plajer.is_cpu) + 'false' * (not plajer.is_cpu))
            for control in plajer.controls:
                file.write('\n    ' + control + ' = ' + str(plajer.controls[control][:-2]))
        file.close()

    def check_teams(self):
        for plajer in self.players:
            if plajer.team > self.team_count:
                plajer.team = 0

    def player_choose_team(self):
        self.get_player_inputs()
        for plajer in self.players:
            if plajer.team != 0:
                if (plajer.controls['shield'][-1]) or (plajer.controls['ability'][-1]):
                    plajer.team = 0
            if plajer.team == 0:
                if plajer.controls['left'][-1]:
                    plajer.team = 1
                elif plajer.controls['right'][-1]:
                    plajer.team = 2
                elif plajer.controls['up'][-1]:
                    plajer.team = 3
                elif plajer.controls['down'][-1]:
                    plajer.team = 4
                if plajer.team > self.team_count:
                    plajer.team = 0

    def check_player_team_event(self, event):
        found_team = 0
        for plajer in self.players:
            for control_key in plajer.controls:
                control = plajer.controls[control_key][:]
                if control[0] == -1:
                    if event.key == control[1]:
                        if plajer.team != 0:
                            if (control_key == 'shield') or (control_key == 'ability'):
                                plajer.team = 0
                                found_team = 1
                        else:
                            if control_key == 'left':
                                plajer.team = 1
                                found_team = 1
                            elif control_key == 'right':
                                plajer.team = 2
                                found_team = 1
                            elif control_key == 'up':
                                plajer.team = 3
                                found_team = 1
                            elif control_key == 'down':
                                plajer.team = 4
                                found_team = 1
                            if plajer.team > self.team_count:
                                plajer.team = 0
        return found_team
    
    def check_player_team_joystick(self, control_type, control, i, si):
        found_team = 0
        for plajer in self.players:
            for pcontrol_key in plajer.controls:
                dokey = 0
                pcontrol = plajer.controls[pcontrol_key]
                if pcontrol[0] != -1:
                    if pcontrol[0] == si:
                        if pcontrol[1] == control_type:
                            if control_type == 'button':
                                if pcontrol[2] == control[i]:
                                    dokey = 1
                            elif control_type == 'axis':
                                if pcontrol[2] == control[i]:
                                    if pcontrol[3] == control[2]:
                                        dokey = 1
                            elif control_type == 'hat':
                                if pcontrol[2] == 0:
                                    if pcontrol[3] == control[i]:
                                        dokey = 1
                            if dokey:
                                if plajer.team != 0:
                                    if (pcontrol_key == 'shield') or (pcontrol_key == 'ability'):
                                        plajer.team = 0
                                        found_team = 1
                                else:
                                    if pcontrol_key == 'left':
                                        plajer.team = 1
                                        found_team = 1
                                    elif pcontrol_key == 'right':
                                        plajer.team = 2
                                        found_team = 1
                                    elif pcontrol_key == 'up':
                                        plajer.team = 3
                                        found_team = 1
                                    elif pcontrol_key == 'down':
                                        plajer.team = 4
                                        found_team = 1
                                    if plajer.team > self.team_count:
                                        plajer.team = 0
        return found_team

    def distribute_players(self):
        team_counts = self.team_count * [0]
        no_teamers = []
        for i in range(0, len(self.players)):
            team = self.players[i].team
            if team <= 0:
                no_teamers.append(i)
            else:
                team_counts[team - 1] += 1
        no_teamers = randomize_list(no_teamers)
        for i in no_teamers:
            ii = unbiased_smallest(team_counts)
            self.players[i].team = ii + 1
            team_counts[ii] += 1

    def detect_team_win(self, tron = 0):
        if tron:
            if len(self.tron_game.death_animations):
                return None
            plajers = self.tron_game.players
        else:
            plajers = self.players
        team_alive_players = self.team_count * [0]
        for plajer in plajers:
            if plajer.alive:
                if not tron and (plajer.team > 0 and plajer.team <= self.team_count):
                    team_alive_players[plajer.team - 1] += 1
                elif tron and (plajer.player.team > 0 and plajer.player.team <= self.team_count):
                    team_alive_players[plajer.player.team - 1] += 1
        alive_team_count = 0
        winning_team = 0
        for i in range(0, len(team_alive_players)):
            alive_players = team_alive_players[i]
            if alive_players > 0:
                alive_team_count += 1
                winning_team = i + 1
        if alive_team_count <= 1:
            return winning_team
        return None

    def reset_editor_tools(self):
        self.tool = 'block'
        self.editor_block_color = 0x777777
        self.editor_block_solid = True
        self.editor_mirroring = False
        self.eraser_size = 60
        self.eraser_rect = [[0, 0], [0, 0]]
        self.mouse_step = 8
        self.editor_rounding = 1
        self.soft_reset_editor_tools()

    def soft_reset_editor_tools(self):
        self.placing_block = False
        self.editor_block_pos = [0, 0]
        self.new_block = [[0, 0], [0, 0]]
        self.new_player_pos = [0, 0]
        self.edit_index = None
        self.edit_index_shifted = None
        self.edited_block = level_block()
        self.edited_player_pos = [0, 0]
        self.edited_background = 0x000000
        self.mouse_last_lmb = 1
        self.mouse_l_wait = True
        self.mouse_last_rmb = 1
        self.mouse_r_wait = True
        self.menu_controls = {'up': 0,
                              'down': 0,
                              'left': 0,
                              'right': 0,
                              'select': 0,
                              'back': 0,
                              'page_entrance': 1,
                              'continual': 1}

    def get_editor_inputs(self):
        self.raw_mouse_input = pygame.mouse.get_pos()
        self.scaled_raw_mouse_input = [self.raw_mouse_input[0] * self.mouse_multiplier[0], self.raw_mouse_input[1] * self.mouse_multiplier[1]]
        self.mouse_pos = [self.scaled_raw_mouse_input[0] / self.surface_size[0] * self.levels[self.level].size[0], self.scaled_raw_mouse_input[1] / self.surface_size[1] * self.levels[self.level].size[1]]
        self.mouse_last_lmb = self.mouse_lmb
        self.mouse_last_rmb = self.mouse_rmb
        self.mouse_lmb = pygame.mouse.get_pressed()[0]
        if self.mouse_l_wait and self.mouse_lmb:
            self.mouse_lmb = 0
        elif self.mouse_l_wait:
            self.mouse_l_wait = False
        self.mouse_rmb = pygame.mouse.get_pressed()[2]
        if self.mouse_r_wait and self.mouse_rmb:
            self.mouse_rmb = 0
        elif self.mouse_r_wait:
            self.mouse_r_wait = False
        pressed_keys = pygame.key.get_pressed()
        self.menu_controls['up'] = pressed_keys[pygame.K_UP]
        self.menu_controls['down'] = pressed_keys[pygame.K_DOWN]
        self.menu_controls['left'] = pressed_keys[pygame.K_LEFT]
        self.menu_controls['right'] = pressed_keys[pygame.K_RIGHT]
        self.menu_controls['back'] = 0
        self.menu_controls['select'] = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.menu_controls['back'] = 1
                elif event.key == pygame.K_RETURN:
                    self.menu_controls['select'] = 1
            elif (event.type == pygame.JOYDEVICEADDED) or (event.type == pygame.JOYDEVICEREMOVED):
                self.reset_joysticks()
            elif (event.type == pygame.WINDOWRESIZED) or (event.type == pygame.WINDOWMOVED) or (event.type == pygame.WINDOWEXPOSED):
                self.update_window_size()

        eraser = 0
        if (self.tool == 'eraser'):
            if self.menu_controls['page_entrance']:
                self.eraser_latch = 1
                self.menu_controls['page_entrance'] = 0
            eraser = 1
        
        for kontroller in self.controllers:
            kontroller.check_inputs(self.menu_controls, [0, 0], self.menu_controls['page_entrance'], 1, eraser)
        self.menu_controls['page_entrance'] = 0

        if eraser:
            if self.eraser_latch:
                if not self.menu_controls['select']:
                    self.eraser_latch = 0
                else:
                    self.menu_controls['select'] = 0

    def run_editor(self):
        self.leraser_rect = [self.eraser_rect[0][:], self.eraser_rect[1][:]]
        self.lnew_player_pos = self.new_player_pos[:]
        self.lnew_block = [self.new_block[0][:], self.new_block[1][:]]
        self.last_block_count = len(self.levels[self.level].blocks)
        self.last_player_count = len(self.levels[self.level].player_poses)

        lvl = self.levels[self.level]
        
        if self.mode_entrance:
            self.mode_entrance = 0
            lvl.render_block_surfaces()
            self.su_all = 1

        if self.menu_controls['up']:
            self.raw_mouse_input = [self.raw_mouse_input[0], self.raw_mouse_input[1] - self.mouse_step]
            if self.raw_mouse_input[1] < 0:
                self.raw_mouse_input[1] = 0
            pygame.mouse.set_pos(self.raw_mouse_input)
        if self.menu_controls['down']:
            self.raw_mouse_input = [self.raw_mouse_input[0], self.raw_mouse_input[1] + self.mouse_step]
            if self.raw_mouse_input[1] > self.display_size[1]:
                self.raw_mouse_input[1] = self.display_size[1] - 1
            pygame.mouse.set_pos(self.raw_mouse_input)
        if self.menu_controls['left']:
            self.raw_mouse_input = [self.raw_mouse_input[0] - self.mouse_step, self.raw_mouse_input[1]]
            if self.raw_mouse_input[0] < 0:
                self.raw_mouse_input[0] = 0
            pygame.mouse.set_pos(self.raw_mouse_input)
        if self.menu_controls['right']:
            self.raw_mouse_input = [self.raw_mouse_input[0] + self.mouse_step, self.raw_mouse_input[1]]
            if self.raw_mouse_input[0] > self.display_size[0]:
                self.raw_mouse_input[0] = self.display_size[0] - 1
            pygame.mouse.set_pos(self.raw_mouse_input)
        
        if self.menu_controls['back']:
            self.do_actions([['editor_display_level'], ['goto', 'editor_menu']])
        
        if self.tool == 'player':
            self.new_player_pos = [round(self.mouse_pos[0] - lvl.player_size[0] / 2), round(self.mouse_pos[1] - lvl.player_size[1] / 2)]
            while 1:
                no_overlap = True
                for block in lvl.blocks:
                    if block.solid:
                        overlap = rect_overlap(self.new_player_pos, lvl.player_size, [0, 0], block.pos, block.size, override = 1)
                        if overlap != [0, 0]:
                            no_overlap = False
                            self.new_player_pos = [self.new_player_pos[0], round(self.new_player_pos[1] + overlap[1])]
                            break
                if no_overlap:
                    for pos in lvl.player_poses:
                        overlap = rect_overlap(self.new_player_pos, lvl.player_size, [0, 0], pos, lvl.player_size, override = 1)
                        if overlap != [0, 0]:
                            no_overlap = False
                            self.new_player_pos = [self.new_player_pos[0], round(self.new_player_pos[1] + overlap[1])]
                            break
                    if no_overlap:
                        break

        if (self.mouse_lmb and not self.mouse_last_lmb) or self.menu_controls['select']:
            if self.tool == 'block':
                if self.placing_block:
                    block = level_block()
                    block.color = self.editor_block_color
                    [block.pos, block.size] = point2size(self.editor_block_pos, self.mouse_pos, self.editor_rounding)
                    block.solid = self.editor_block_solid
                    self.placing_block = False
                    if (block.size[0] > 0) and (block.size[1] > 0):
                        lvl.blocks.append(block)
                        if self.editor_mirroring:
                            blokk = level_block()
                            blokk.copy_from(block)
                            blokk.pos = [lvl.size[0] - block.pos[0] - block.size[0], block.pos[1]]
                            lvl.blocks.append(blokk)
                        lvl.render_block_surfaces()
                else:
                    self.editor_block_pos = [round(self.mouse_pos[0]), round(self.mouse_pos[1])]
                    self.placing_block = True
            elif self.tool == 'player':
                if self.new_player_pos[1] + lvl.player_size[1] > 0:
                    lvl.player_poses.append(self.new_player_pos)
                    if self.editor_mirroring:
                        lvl.player_poses.append([lvl.size[0] - self.new_player_pos[0] - lvl.player_size[0], self.new_player_pos[1]])
            elif self.tool == 'edit':
                edit_type = 'background'
                self.edited_background = lvl.background_color
                self.edit_index = None
                self.edit_index_shifted = None
                for i in range(0, len(lvl.player_poses)):
                    h = len(lvl.player_poses) - i - 1
                    if in_rect(self.mouse_pos, lvl.player_poses[h], lvl.player_size, lvl):
                        edit_type = 'player'
                        self.edit_index = h
                        self.edit_index_shifted = h
                        self.edited_player_pos = lvl.player_poses[h][:]
                        break
                if edit_type != 'player':
                    for i in range(0, len(lvl.blocks)):
                        h = len(lvl.blocks) - i - 1
                        if in_rect(self.mouse_pos, lvl.blocks[h].pos, lvl.blocks[h].size, lvl):
                            edit_type = 'block'
                            self.edit_index = h
                            self.edit_index_shifted = h
                            self.edited_block = level_block()
                            self.edited_block.copy_from(lvl.blocks[self.edit_index])
                            break
                self.do_actions([['goto', 'edit_' + edit_type]])

        if self.tool == 'eraser':
            p = [self.mouse_pos[0] - self.eraser_size * lvl.scale[0] / 2, self.mouse_pos[1] - self.eraser_size * lvl.scale[1] / 2]
            s = [self.eraser_size * lvl.scale[0], self.eraser_size * lvl.scale[1]]
            for i in range(0, 2):
                if p[i] < 0:
                    s[i] = p[i] + s[i]
                    p[i] = 0
                elif p[i] + s[i] > lvl.size[i]:
                    s[i] = lvl.size[i] - p[i]
            self.eraser_rect = [p, s]
            if self.mouse_lmb or self.menu_controls['select']:
                player_poses_to_delete = []
                for i in range(0, len(lvl.player_poses)):
                    if rect_overlap(self.eraser_rect[0], self.eraser_rect[1], [0, 0], lvl.player_poses[i], lvl.player_size, lwl = lvl) != [0, 0]:
                        player_poses_to_delete.insert(0, i)
                for index in player_poses_to_delete:
                    lvl.player_poses.pop(index)
                blocks_to_delete = []
                for i in range(0, len(lvl.blocks)):
                    if rect_overlap(self.eraser_rect[0], self.eraser_rect[1], [0, 0], lvl.blocks[i].pos, lvl.blocks[i].size, lwl = lvl) != [0, 0]:
                        blocks_to_delete.insert(0, i)
                for index in blocks_to_delete:
                    lvl.blocks.pop(index)
                if len(blocks_to_delete):
                    lvl.render_block_surfaces()
            
        if self.mouse_lmb or self.menu_controls['select']:
            self.su_all = 1

        if self.mouse_rmb and not self.mouse_last_rmb:
            self.su_all = 1
            if self.placing_block:
                self.placing_block = False
            else:
                found_player_pos = False
                for i in range(0, len(lvl.player_poses)):
                    h = len(lvl.player_poses) - i - 1
                    if in_rect(self.mouse_pos, lvl.player_poses[h], lvl.player_size, lvl):
                        lvl.player_poses.pop(h)
                        lvl.render_block_surfaces()
                        found_player_pos = True
                        break
                if not found_player_pos:
                    for i in range(0, len(lvl.blocks)):
                        h = len(lvl.blocks) - i - 1
                        if in_rect(self.mouse_pos, lvl.blocks[h].pos, lvl.blocks[h].size, lvl):
                            lvl.blocks.pop(h)
                            lvl.render_block_surfaces()
                            break
        
        self.editor_display_level(True)

    def editor_display_level(self, show_extra = False):
        lvl = self.levels[self.level]
        
        lvl.surface = pygame.Surface(lvl.size)
        lvl.surface.fill(lvl.background_color)

        lvl.surface.blit(lvl.surface_unsolid, [0, 0])
        lvl.surface.blit(lvl.surface_solid, [0, 0])
        if self.last_block_count < len(lvl.blocks):
            self.editor_append_su_rects([lvl.blocks[-1].pos, lvl.blocks[-1].size])

        for pos in lvl.player_poses:
            pygame.draw.rect(lvl.surface, 0xff0000, [pos, lvl.player_size])
            pygame.draw.rect(lvl.surface, 0xff8800, [[pos[0] + lvl.player_size[0] * 0.2, pos[1] + lvl.player_size[1] * 0.2], [lvl.player_size[0] * 0.6, lvl.player_size[1] * 0.6]])
        if self.last_player_count < len(lvl.player_poses):
            self.editor_append_su_rects([lvl.player_poses[-1], lvl.player_size])

        if show_extra:
            if self.tool == 'eraser':
                pygame.draw.rect(lvl.surface, 0xffbbbb, self.eraser_rect)
                self.editor_append_su_rects(self.leraser_rect)
                self.editor_append_su_rects(self.eraser_rect)
            elif self.tool == 'player':
                red_player = [self.new_player_pos, lvl.player_size]
                pygame.draw.rect(lvl.surface, 0xff0000, red_player)
                orange_player = [[self.new_player_pos[0] + lvl.player_size[0] * 0.2, self.new_player_pos[1] + lvl.player_size[1] * 0.2], [lvl.player_size[0] * 0.6, lvl.player_size[1] * 0.6]]
                pygame.draw.rect(lvl.surface, 0xff8800, orange_player)
                self.editor_append_su_rects([self.lnew_player_pos, lvl.player_size])
                self.editor_append_su_rects(red_player)
            if self.placing_block:
                self.new_block = point2size(self.editor_block_pos, self.mouse_pos, self.editor_rounding)
                pygame.draw.rect(lvl.surface, self.editor_block_color, self.new_block)
                self.editor_append_su_rects(self.lnew_block)
                self.editor_append_su_rects(self.new_block)
            if self.editor_mirroring:
                if self.tool == 'player':
                    pygame.draw.rect(lvl.surface, 0xff0000, reflect_rect(red_player, lvl.size))
                    pygame.draw.rect(lvl.surface, 0xff8800, reflect_rect(orange_player, lvl.size))
                    self.editor_append_su_rects(reflect_rect([self.lnew_player_pos, lvl.player_size], lvl.size))
                    self.editor_append_su_rects(reflect_rect(red_player, lvl.size))
                if self.placing_block:
                    pygame.draw.rect(lvl.surface, self.editor_block_color, reflect_rect(self.new_block, lvl.size))
                    self.editor_append_su_rects(reflect_rect(self.lnew_block, lvl.size))
                    self.editor_append_su_rects(reflect_rect(self.new_block, lvl.size))
        self.surface.blit(pygame.transform.scale(lvl.surface, self.surface_size), [0, 0])

    def editor_append_su_rects(self, rect):
        pad = self.su_rect_pad
        lvl = self.levels[self.level]
        p = [lvl.inv_scale[0] * rect[0][0] - pad, lvl.inv_scale[1] * rect[0][1] - pad]
        s = [lvl.inv_scale[0] * rect[1][0] + 2 * pad, lvl.inv_scale[1] * rect[1][1] + 2 * pad]
        #self.su_rects.append([p, s])
        self.su_rects.append(rect)

    def load_secrets(self):
        file = open(os.path.join(self.cwd, 'secrets.txt'), encoding = 'utf-16')
        file_string = file.read()
        self.secrets = shift_chars(file_string, -1).split('\n')
        file.close()

    def get_snake_inputs(self):
        self.snake_game.get_inputs(self.players, self.controllers, self.joysticks, self.joystick_threshold, self.surface_size, self.su_rects)

    def play_snake(self):
        if self.mode_entrance:
            self.mode_entrance = 0
            self.su_all = 1
        if self.snake_game.alive:
            if self.snake_game.counter >= self.tick_speed / self.snake_game.tick_speed:
                self.snake_game.update_snake(self.surface_size, self.su_rects)
            if (self.snake_game.counter == 0) or (self.snake_game.grass_change_counter == 0):
                self.snake_game.display_snake(self.surface)
                self.surface_screenshot = self.surface.copy()
            else:
                self.surface.blit(self.surface_screenshot, [0, 0])
        else:
            self.snake_game.update_death()
            self.snake_game.display_death(self.surface, self.su_rects)
            if self.snake_game.ask_for_quit():
                self.secret = self.secrets[random.randint(0, len(self.secrets) - 1)]
                self.snake_scores.append([self.snake_game.score, self.snake_game.name, self.snake_game.snake_head])
                self.snake_scores.sort(reverse = 1)
                while len(self.snake_scores) > 10:
                    self.snake_scores.pop()
                self.save_snake_scores()
                self.do_actions([['goto', 'snake_results']])
        if self.snake_game.quit_squish:
            self.running = 0
        if self.snake_game.update_window_size:
            self.snake_game.update_window_size = 0
            self.update_window_size()
        if self.snake_game.reset_joysticks:
            self.snake_game.reset_joysticks = 0
            self.reset_joysticks()

    def load_snake_scores(self):
        # Each entry should be: [score, name, color]
        file = open(os.path.join(self.cwd, 'snake_scores.txt'), encoding = 'utf-8')
        self.snake_scores = []
        for line in file:
            values = line.split(', ')
            self.snake_scores.append([int(values[0]), values[1], int(values[2], 16)])
        self.snake_scores.sort()
        file.close()

    def save_snake_scores(self):
        file = open(os.path.join(self.cwd, 'snake_scores.txt'), mode = 'w', encoding = 'utf-8')
        for i in range(0, len(self.snake_scores)):
            if i != 0:
                file.write('\n')
            score = self.snake_scores[i]
            file.write(str(score[0]) + ', ')
            file.write(score[1] + ', ')
            file.write('0x' + hex(score[2])[2:].rjust(6, '0'))
        file.close()

    def get_scythe_inputs(self):
        self.scythe_game.get_inputs(self.controllers)

    def play_scythe(self):
        if self.mode_entrance:
            self.mode_entrance = 0
            self.su_all = 1
        if self.scythe_game.running:
            if not self.scythe_game.game_over:
                self.scythe_game.update_scythe(self.surface_size, self.su_rects)
            elif len(self.scythe_game.death_particles) <= 0:
                self.scythe_game.running = 0
            self.scythe_game.display_scythe(self.surface, self.su_rects, self)
        else:
            self.secret = self.secrets[random.randint(0, len(self.secrets) - 1)]
            self.scythe_scores.append(round(self.scythe_game.score))
            self.scythe_scores.sort(reverse = 1)
            while len(self.scythe_scores) > 10:
                self.scythe_scores.pop()
            self.save_scythe_scores()
            self.do_actions([['goto', 'scythe_results']])
        if self.scythe_game.quit_squish:
            self.running = 0
        if self.scythe_game.update_window_size:
            self.scythe_game.update_window_size = 0
            self.update_window_size()
        if self.scythe_game.reset_joysticks:
            self.scythe_game.reset_joysticks = 0
            self.reset_joysticks()

    def load_scythe_scores(self):
        # Each entry should be an integer score
        file = open(os.path.join(self.cwd, 'scythe_scores.txt'), encoding = 'utf-8')
        self.scythe_scores = []
        for line in file:
            self.scythe_scores.append(int(line))
        self.scythe_scores.sort()
        file.close()

    def save_scythe_scores(self):
        file = open(os.path.join(self.cwd, 'scythe_scores.txt'), mode = 'w', encoding = 'utf-8')
        for i in range(0, len(self.scythe_scores)):
            if i != 0:
                file.write('\n')
            file.write(str(self.scythe_scores[i]))
        file.close()

    def show_secret(self):
        [img, s] = self.text2img(self.secret, 0, 'couriernew', 32, 1)
        pygame.draw.rect(self.surface, 0x5e3926, [[self.surface_size[0] - 40 - s[0], self.surface_size[1] - 30 - s[1]], [s[0] + 28, s[1] + 20]])
        pygame.draw.rect(self.surface, 0xab6a47, [[self.surface_size[0] - 34 - s[0], self.surface_size[1] - 24 - s[1]], [s[0] + 16, s[1] + 8]])
        self.surface.blit(img, [self.surface_size[0] - 26 - s[0], self.surface_size[1] - 20 - s[1]])

    def play_tron(self):
        if self.mode_entrance:
            self.mode_entrance = 0
            self.su_all = 1
        self.tron_game.run()
        self.tron_game.display(self.su_rects)
        self.surface.blit(pygame.transform.scale(self.tron_game.surface, self.surface_size), [0, 0])
        if self.team_count == 0:
            if self.tron_game.ask_for_quit():
                if self.tron_game.winner:
                    self.winner_index = self.players.index(self.tron_game.winner)
                    self.players[self.winner_index].wins += 1
                else:
                    self.winner_index = None
                self.do_actions([['goto', 'end_tron']])
        else:
            self.winning_team = self.detect_team_win(1)
            if self.winning_team != None:
                for plajer in self.tron_game.players:
                    if plajer.player.team == self.winning_team:
                        plajer.player.wins += 1
                self.do_actions([['goto', 'end_tron']])

    def update_window_size(self, update_scales = 1):
        self.su_all = 1
        self.display_size = pygame.display.get_window_size()
        self.mouse_multiplier = [self.initial_size[0] / self.display_size[0], self.initial_size[1] / self.display_size[1]]
        if update_scales:
            self.screen_scales = [self.display_size[0] / self.real_display_size[0], self.display_size[1] / self.real_display_size[1]]

    def toggle_fullscreen(self):
        if self.fullscreen:
            pygame.display.set_mode([self.screen_scales[0] * self.display_size[0], self.screen_scales[1] * self.display_size[1]], flags = pygame.RESIZABLE)
            pygame.display.set_mode([self.screen_scales[0] * self.display_size[0], self.screen_scales[1] * self.display_size[1]], flags = pygame.RESIZABLE)
            self.fullscreen = 0
        else:
            pygame.display.set_mode(flags = pygame.FULLSCREEN)
            self.fullscreen = 1
        self.update_window_size(0)

    def toggle_resolution(self):
        self.resolution
        self.resolutions
        if self.resolutions.count(self.resolution):
            i = self.resolutions.index(self.resolution)
            self.resolution = self.resolutions[(i + 1) % len(self.resolutions)]
        else:
            self.resolution = self.resolutions[-1]
        self.restart_display(0)
        self.update_window_size()
        self.mode_entrance = 1

    def text2img(self, text, color, font, font_size, is_bold):
        font = pygame.font.SysFont(font, round(self.font_multiplier * font_size), is_bold)
        rendered_text = font.render(text, False, color)
        text_size = font.size(text)
        return rendered_text, text_size

    def scale(self, rect, is1, s2):
        s1 = [is1[0] + (is1[0] == 0), is1[1] + (is1[1] == 0)]
        p = [round(rect[0][0] * s2[0] / s1[0] - self.su_rect_pad), round(rect[0][1] * s2[1] / s1[1] - self.su_rect_pad)]
        s = [round(rect[1][0] * s2[0] / s1[0] + 2 * self.su_rect_pad), round(rect[1][1] * s2[1] / s1[1] + 2 * self.su_rect_pad)]
        return [p, s]

    def update(self):
        if self.mode != 'squish' or 1: # [Redact] this
            if self.show_fps and not self.menu_controls['page_entrance']:
                m = 0.5 * (self.resolution[0] / 1920 + self.resolution[1] / 1080)
                if ((self.mode == 'tron') or (self.page == 'end_tron') or (self.page == 'pause_tron')) and not (self.mode == 'squish'):
                    p = [70 * m, 70 * m]
                else:
                    p = [16 * m, 16 * m]
                [fps_img, s] = self.text2img(str(0.1 * round(10 * self.clock.get_fps()))[0:4], 0, 'couriernew', 32, 1)
                self.surface.blit(fps_img, p)
                if (self.mode == 'squish') or (self.mode == 'editor'):
                    self.su_rects.append(self.scale([p, s], self.resolution, self.levels[self.level].size))
                elif self.mode == 'tron':
                    self.su_rects.append(self.scale([p, s], self.surface_size, [1920, 1080]))
                else:
                    self.su_rects.append([p, s])
            
            # [Redact] this
            if (self.mode == 'squish') and not self.mode_entrance and 0:
                m = 0.5 * (self.resolution[0] / 1920 + self.resolution[1] / 1080)
                p1 = [self.dba1[0] * m, self.dba1[1] * m]
                p2 = [self.dba2[0] * m, self.dba2[1] * m]
                #pygame.draw.rect(self.surface, 0xffff00, [p1, [40, 40]])
                #pygame.draw.rect(self.surface, 0x00ffff, [p2, [40, 40]])

                [dbt_img, s] = self.text2img('Kill: ' * self.tar.dir + 'Flee: ' * (not self.tar.dir) + self.tar.type, 0, 'couriernew', 32, 1)
                p = [self.plajer_pos[0] * m, self.plajer_pos[1] * m]
                self.surface.blit(dbt_img, p)
                for target in self.pot_tar:
                    [target_img, s] = self.text2img('Kill: ' * target.dir + 'Flee: ' * (not target.dir) + str(round(target.weight)), 0, 'couriernew', 32, 1)
                    p2 = target.pos
                    p2 = [p2[0] * m - 35, p2[1] * m]
                    if target.dir:
                        p2[1] += 5
                    else:
                        p2[0] += -15
                        p2[1] += -5
                    self.surface.blit(target_img, p2)
                self.su_all = 1
            
            self.display.blit(pygame.transform.scale(self.surface, self.display_size), [0, 0])

            # Only blit some of the screen
            if self.su_all:
                pygame.display.update()
            else:
                ssu_rects = []
                usu_rects = remove_redundancy(self.su_rects)
                for rect in usu_rects:
                    if (self.mode == 'squish') or (self.mode == 'editor'):
                        ssu_rects.append(self.scale(rect, self.levels[self.level].size, self.display_size))
                    elif self.mode == 'tron':
                        ssu_rects.append(self.scale(rect, [1920, 1080], self.display_size))
                    else:
                        ssu_rects.append(self.scale(rect, self.surface_size, self.display_size))
                pygame.display.update(ssu_rects)
        self.su_rects = []
        self.su_all = self.menu_controls['page_entrance']

        self.page = self.next_page
        self.clock.tick(self.tick_speed)

    def close(self):
        pygame.quit()

class page():
    def __init__(self, file, display_size, game_instance):
        self.blocks = []
        self.buttons = []
        self.controls = []
        self.lists = []
        self.sliders = []
        self.settings = []
        objekt_type = 0
        objekt = 0
        for line in file:
            no_spaces_line = line.replace(' ', '')
            no_comment_line = no_spaces_line.split('#')[0]
            no_return_line = no_comment_line.replace('\n', '')
            split_line = no_return_line.split('=')
            properky = split_line[0]
            value = split_line[-1]
            if properky == 'block':
                if objekt != 0:
                    self.append_objekt(objekt, objekt_type)
                objekt_type = 'block'
                objekt = menu_block()
            elif properky == 'button':
                if objekt != 0:
                    self.append_objekt(objekt, objekt_type)
                objekt_type = 'button'
                objekt = menu_button()
            elif properky == 'control':
                if objekt != 0:
                    self.append_objekt(objekt, objekt_type)
                objekt_type = 'control'
                objekt = menu_control()
            elif properky == 'list':
                if objekt != 0:
                    self.append_objekt(objekt, objekt_type)
                objekt_type = 'list'
                objekt = menu_list()
            elif properky == 'slider':
                if objekt != 0:
                    self.append_objekt(objekt, objekt_type)
                objekt_type = 'slider'
                objekt = menu_slider()
            elif properky == 'type':
                objekt.type = value
            elif properky == 'button_pos':
                xy = findxy(no_return_line)
                objekt.button_pos = [int(xy[0]), int(xy[1])]
            elif properky == 'size':
                objekt.size = findxy(no_return_line, display_size)
            elif properky == 'pos':
                objekt.pos = findxy(no_return_line, display_size, [0, 0], objekt.size)
            elif properky == 'color':
                objekt.color = int(value, 16)
            elif properky == 'color_main':
                objekt.color_main = int(value, 16)
                objekt.color = objekt.color_main
            elif properky == 'color_alt':
                objekt.color_alt = int(value, 16)
            elif properky == 'dynamic_color':
                objekt.dynamic_color = value.split(':')
            elif properky == 'alpha':
                objekt.alpha = int(value)
            elif properky == 'entry_size':
                objekt.entry_size = findxy(no_return_line, display_size)
            elif properky == 'entry_spacing':
                objekt.entry_spacing = findx(value, objekt.size[1])
            elif properky == 'entry_color':
                objekt.entry_color = int(value, 16)
            elif properky == 'image_size':
                objekt.image_size = findxy(value, objekt.entry_size)
            elif properky == 'image_pos':
                objekt.image_pos = findxy(value, objekt.entry_size, [0, 0], objekt.image_size)
            elif properky == 'frame_size':
                objekt.frame_size = findxy(value, objekt.image_size)
            elif properky == 'frame_pos':
                objekt.frame_pos = findxy(value, objekt.image_size, objekt.image_pos, objekt.frame_size)
            elif properky == 'frame_color':
                objekt.frame_color = int(value, 16)
            elif properky == 'only_last':
                objekt.only_last = (value.lower() == 'true') or (value == '1')
            elif properky == 'team':
                objekt.team = int(value)
            elif properky == 'active_color':
                objekt.active_color = int(value, 16)
            elif properky == 'text_active_color':
                objekt.text_active_color = int(value, 16)
            elif properky == 'text':
                objekt.text = line.split("'")[1]
            elif properky == 'text_variable':
                objekt.text_variable = value
            elif properky == 'text_variable_char_limit':
                objekt.text_variable_char_limit = int(value)
            elif properky == 'text_color':
                objekt.text_color = (int(value[2:4], 16), int(value[4:6], 16), int(value[6:8], 16))
            elif properky == 'text_bold':
                objekt.text_bold = (value.lower() == 'true') or (value == '1')
            elif properky == 'text_font':
                objekt.text_font = value
            elif properky == 'text_size':
                objekt.text_size = int(value)
                [objekt.text_image, objekt.text_image_size] = game_instance.text2img(objekt.text, objekt.text_color, objekt.text_font, objekt.text_size, objekt.text_bold)
            elif properky == 'text_pos':
                if objekt_type == 'list':
                    objekt.text_pos = findxy(no_return_line, objekt.entry_size, [0, 0], objekt.text_image_size)
                else:
                    objekt.text_pos_string = no_return_line
                    objekt.text_pos = findxy(no_return_line, objekt.size, objekt.pos, objekt.text_image_size)
                    objekt.text_window_size = [objekt.size[0] - objekt.text_pos[0] + objekt.pos[0], objekt.size[1] - objekt.text_pos[1] + objekt.pos[1]]
            elif properky == 'text_limit':
                objekt.text_limit = findxy(no_return_line, objekt.entry_size)
            elif properky == 'wins_pos':
                objekt.wins_pos = findxy(no_return_line, objekt.entry_size, [0, 0], objekt.text_image_size)
            elif properky == 'kills_pos':
                objekt.kills_pos = findxy(no_return_line, objekt.entry_size, [0, 0], objekt.text_image_size)
            elif properky == 'text_dynamic_pos':
                objekt.text_dynamic_pos = (value.lower() == 'true') or (value == '1')
            elif properky == 'text_input_limit':
                objekt.text_input_limi = int(value)
            elif properky == 'trigger':
                objekt.trigger = value
            elif properky == 'action':
                split_value = value.split(':')
                objekt.actions.append(split_value)
                if split_value[0:3] == ['set', 'level', 'background_color']:
                    color_value = split_value[3]
                    objekt.text_color = (int(color_value[2:4], 16), int(color_value[4:6], 16), int(color_value[6:8], 16))
            elif properky == 'value':
                objekt.value = value
            elif properky == 'selectable':
                objekt.selectable = (value.lower() == 'true') or (value == '1')
            elif properky == 'select_color':
                objekt.select_color = int(value, 16)
            elif properky == 'select_pos':
                xy = findxy(no_return_line)
                objekt.select_pos = [int(xy[0]), int(xy[1])]
            elif properky == 'dont_direct_horizontal_cursor':
                self.settings.append(properky)
            elif properky == 'dont_direct_vertical_cursor':
                self.settings.append(properky)
            elif properky == 'take_screenshot':
                self.settings.append(properky)
            elif properky == 'page_pause':
                self.settings.append(properky)
            elif properky == 'rank_pos':
                objekt.rank_pos = findxy(no_return_line, objekt.entry_size, [0, 0], objekt.text_image_size)
            elif properky == 'score_pos':
                objekt.score_pos = findxy(no_return_line, objekt.entry_size, [0, 0], objekt.text_image_size)
            elif properky == 'min_value':
                objekt.min_value = int(value)
            elif properky == 'max_value':
                objekt.max_value = int(value)
            elif properky == 'knob_color':
                objekt.knob_color = int(value, 16)
            elif properky == 'left_color':
                objekt.left_color = int(value, 16)
            elif properky == 'right_color':
                objekt.right_color = int(value, 16)
            elif properky == 'slider_size':
                objekt.slider_size = findxy(no_return_line, objekt.size)
            elif properky == 'slider_pos':
                objekt.slider_pos = findxy(no_return_line, objekt.size, objekt.pos, objekt.slider_size)
        self.append_objekt(objekt, objekt_type)
        self.button_array = [[0]]
        for button in self.buttons:
            for i in range(len(self.button_array), max(button.button_pos) + 1):
                self.button_array.append([0])
                for ii in range(0, len(self.button_array[0])):
                    self.button_array[ii].append(0)
                    self.button_array[-1].append(0)
            self.button_array[button.button_pos[0]][button.button_pos[1]] = 1
        for lisk in self.lists:
            if lisk.selectable:
                for i in range(len(self.button_array), max(lisk.select_pos) + 1):
                    self.button_array.append([0])
                    for ii in range(0, len(self.button_array[0])):
                        self.button_array[ii].append(0)
                        self.button_array[-1].append(0)
                self.button_array[lisk.select_pos[0]][lisk.select_pos[1]] = 1
        for slider in self.sliders:
            for i in range(len(self.button_array), max(slider.button_pos) + 1):
                self.button_array.append([0])
                for ii in range(0, len(self.button_array[0])):
                    self.button_array[ii].append(0)
                    self.button_array[-1].append(0)
            self.button_array[slider.button_pos[0]][slider.button_pos[1]] = 1

    def append_objekt(self, objekt, objekt_type):
        if objekt_type == 'block':
            self.blocks.append(objekt)
        elif objekt_type == 'button':
            self.buttons.append(objekt)
        elif objekt_type == 'control':
            self.controls.append(objekt)
        elif objekt_type == 'list':
            self.lists.append(objekt)
        elif objekt_type == 'slider':
            self.sliders.append(objekt)

class menu_block():
    def __init__(self):
        self.size = [0, 0]
        self.pos = [0, 0]
        self.color = -1
        self.color_main = -1
        self.color_alt = -1
        self.dynamic_color = None
        self.alpha = 255
        self.text = ''
        self.text_variable = ''
        self.text_variable_char_limit = None
        self.text_color = 0x000000
        self.text_bold = 0
        self.text_font = 'couriernew'
        self.text_size = None
        self.text_image = 0
        self.text_image_size = [0, 0]
        self.text_pos = [0, 0]
        self.text_dynamic_pos = 0
        self.text_pos_string = ''

class menu_button():
    def __init__(self):
        self.button_pos = [0, 0]
        self.size = [0, 0]
        self.pos = [0, 0]
        self.color = -1
        self.active_color = -1
        self.dynamic_color = None
        self.text_active_color = -1
        self.text = ''
        self.text_variable = ''
        self.text_variable_char_limit = None
        self.text_input = ''
        self.text_color = 0
        self.text_bold = 0
        self.text_font = 'couriernew'
        self.text_size = None
        self.text_image = 0
        self.text_image_size = [0, 0]
        self.text_window_size = [0, 0]
        self.text_pos = [0, 0]
        self.text_dynamic_pos = 0
        self.text_pos_string = ''
        self.text_input_limit = -1
        self.actions = []
        self.value = 0

class menu_control():
    def __init__(self):
        self.trigger = 0
        self.actions = []

class menu_list():
    def __init__(self):
        self.type = ''
        self.size = [0, 0]
        self.pos = [0, 0]
        self.color = 0
        self.entry_size = [0, 0]
        self.entry_spacing = 0
        self.entry_color = 0
        self.image_size = [0, 0]
        self.image_pos = [0, 0]
        self.frame_size = [0, 0]
        self.frame_pos = [0, 0]
        self.frame_color = 0
        self.only_last = 0
        self.team = None
        self.text = ''
        self.text_color = 0
        self.text_bold = 0
        self.text_font = 'couriernew'
        self.text_size = None
        self.text_pos = [0, 0]
        self.text_limit = None
        self.wins_pos = [0, 0]
        self.kills_pos = [0, 0]
        self.rank_pos = [0, 0]
        self.score_pos = [0, 0]
        self.scroll_value = 0
        self.selectable = 0
        self.select_color = 0
        self.select_pos = 0
        self.actions = []
    
    def scroll(self, scroll_distance, entry_count):
        self.scroll_value += scroll_distance
        scroll_limit = -1 * (entry_count * self.entry_size[1] + (entry_count - 1) * self.entry_spacing - self.size[1])
        if self.scroll_value < scroll_limit:
            self.scroll_value = scroll_limit
        if self.scroll_value > 0:
            self.scroll_value = 0

class menu_slider():
    def __init__(self):
        self.button_pos = [0, 0]
        self.size = [0, 0]
        self.pos = [0, 0]
        self.color = -1
        self.active_color = -1
        self.text = ''
        self.text_variable = ''
        self.text_variable_char_limit = None
        self.text_color = 0
        self.text_bold = True
        self.text_font = 'couriernew'
        self.text_size = 32
        self.text_image = None
        self.text_image_size = [0, 0]
        self.text_window_size = [0, 0]
        self.text_pos = [0, 0]
        self.text_pos_string = ''
        self.actions = []
        self.value = 0

        self.min_value = 0
        self.max_value = 100
        self.knob_color = 0
        self.left_color = 0x555555
        self.right_color = 0x707070
        self.slider_size = [0, 0]
        self.slider_pos = [0, 0]
        self.percent = 1

    def update_knob_pos(self, value):
        if self.max_value - self.min_value != 0:
            self.percent = (value - self.min_value) / (self.max_value - self.min_value)
        else:
            self.percent = 1

class controller():
    def __init__(self, joystick, joystick_threshold):
        self.joystick = joystick
        self.joystick_threshold = joystick_threshold
        self.flick_pause = 0.02
        self.flick_timestamp = [time.time() - self.flick_pause, time.time() - self.flick_pause]
        # Control: [new_value, old_value, axis_direction, input_sources]
        self.controls = {'up': [0, 0, -1, pygame.CONTROLLER_AXIS_LEFTY, pygame.CONTROLLER_BUTTON_DPAD_UP, (0, 1)],
                         'down': [0, 0, 1, pygame.CONTROLLER_AXIS_LEFTY, pygame.CONTROLLER_BUTTON_DPAD_DOWN, (0, -1)],
                         'left': [0, 0, -1, pygame.CONTROLLER_AXIS_LEFTX, pygame.CONTROLLER_BUTTON_DPAD_LEFT, (-1, 0)],
                         'right': [0, 0, 1, pygame.CONTROLLER_AXIS_LEFTX, pygame.CONTROLLER_BUTTON_DPAD_RIGHT, (1, 0)],
                         'jump': [0, 0, -1, pygame.CONTROLLER_AXIS_LEFTY, pygame.CONTROLLER_BUTTON_A, pygame.CONTROLLER_BUTTON_B],
                         'shield': [0, 0, 2, pygame.CONTROLLER_AXIS_TRIGGERRIGHT, pygame.CONTROLLER_AXIS_TRIGGERLEFT, pygame.CONTROLLER_BUTTON_RIGHTSHOULDER, pygame.CONTROLLER_BUTTON_LEFTSHOULDER],
                         'select': [0, 0, 0, pygame.CONTROLLER_BUTTON_A, pygame.CONTROLLER_BUTTON_START],
                         'back': [0, 0, 0, pygame.CONTROLLER_BUTTON_B, pygame.CONTROLLER_BUTTON_BACK]}

    def check_inputs(self, game, dir_override = 0, select_override = 0, si = None):
        menu_controls = game.menu_controls
        menu_input_delay_index = game.menu_input_delay_index
        is_first_frame = game.menu_controls['page_entrance']
        teaming = game.teaming
        for control in self.controls:
            self.controls[control][1] = self.controls[control][0]
            self.controls[control][0] = 0
            for i in range(3, len(self.controls[control])):
                if abs(self.controls[control][2]) > i - 3:
                    if self.joystick.get_numaxes() > self.controls[control][i]:
                        if ((1 - 3 * (self.controls[control][2] < 0)) * self.joystick.get_axis(self.controls[control][i]) >= self.joystick_threshold):
                            self.controls[control][0] = 1
                            if teaming and game.check_player_team_joystick('axis', self.controls[control], i, si):
                                self.controls[control][1] = 1
                            break
                elif type(self.controls[control][i]) == type(tuple()):
                    if self.joystick.get_numhats() > 0:
                        if self.joystick.get_hat(0) == self.controls[control][i]:
                            self.controls[control][0] = 1
                            if teaming and game.check_player_team_joystick('hat', self.controls[control], i, si):
                                self.controls[control][1] = 1
                            break
                elif self.joystick.get_numbuttons() > self.controls[control][i]:
                    if self.joystick.get_button(self.controls[control][i]):
                        self.controls[control][0] = 1
                        if control != 'jump':
                            if teaming and game.check_player_team_joystick('button', self.controls[control], i, si):
                                self.controls[control][1] = 1
                        break
            
            if (control == 'up') or (control == 'down'):
                if self.controls[control][1] and not self.controls[control][0]:
                    self.flick_timestamp[1] = time.time()
                    self.controls['up'][0] = 0
                    self.controls['up'][1] = 1
                    self.controls['down'][0] = 0
                    self.controls['down'][1] = 1
                if not self.controls[control][1] and self.controls[control][0]:
                    timestamp = time.time()
                    if (timestamp > self.flick_timestamp[1]) and (timestamp < self.flick_timestamp[1] + self.flick_pause):
                        self.controls[control][0] = 0
                        self.controls[control][1] = 1
            elif (control == 'left') or (control == 'right'):
                if self.controls[control][1] and not self.controls[control][0]:
                    self.flick_timestamp[0] = time.time()
                    self.controls['left'][0] = 0
                    self.controls['left'][1] = 1
                    self.controls['right'][0] = 0
                    self.controls['right'][1] = 1
                if not self.controls[control][1] and self.controls[control][0]:
                    timestamp = time.time()
                    if (timestamp > self.flick_timestamp[0]) and (timestamp < self.flick_timestamp[0] + self.flick_pause):
                        self.controls[control][0] = 0
                        self.controls[control][1] = 1

        for control in self.controls:
            if not is_first_frame:
                if self.controls[control][0] ^ self.controls[control][1]:
                    menu_controls[control] = self.controls[control][0]
                    if (control == 'up') or (control == 'down'):
                        menu_input_delay_index[1] = 0
                    elif (control == 'left') or (control == 'right'):
                        menu_input_delay_index[0] = 0
                if dir_override:
                    if (control == 'up') or (control == 'down') or (control == 'left') or (control == 'right'):
                        menu_controls[control] = self.controls[control][0]
                if select_override:
                    if (control == 'select'):
                        menu_controls[control] = self.controls[control][0]
    
    def check_snake_inputs(self, new_dir):
        for control in self.controls:
            self.controls[control][1] = self.controls[control][0]
            self.controls[control][0] = 0
            for i in range(3, len(self.controls[control])):
                if abs(self.controls[control][2]) > i - 3:
                    if self.joystick.get_numaxes() > self.controls[control][i]:
                        if ((1 - 3 * (self.controls[control][2] < 0)) * self.joystick.get_axis(self.controls[control][i]) >= self.joystick_threshold):
                            self.controls[control][0] = 1
                            break
                elif type(self.controls[control][i]) == type(tuple()):
                    if self.joystick.get_numhats() > 0:
                        if self.joystick.get_hat(0) == self.controls[control][i]:
                            self.controls[control][0] = 1
                            break
                elif self.joystick.get_numbuttons() > self.controls[control][i]:
                    if self.joystick.get_button(self.controls[control][i]):
                        self.controls[control][0] = 1
                        break
            
            if (control == 'up') or (control == 'down'):
                if self.controls[control][1] and not self.controls[control][0]:
                    self.flick_timestamp[1] = time.time()
                    self.controls['up'][0] = 0
                    self.controls['up'][1] = 1
                    self.controls['down'][0] = 0
                    self.controls['down'][1] = 1
                if not self.controls[control][1] and self.controls[control][0]:
                    timestamp = time.time()
                    if (timestamp > self.flick_timestamp[1]) and (timestamp < self.flick_timestamp[1] + self.flick_pause):
                        self.controls[control][0] = 0
                        self.controls[control][1] = 1
            elif (control == 'left') or (control == 'right'):
                if self.controls[control][1] and not self.controls[control][0]:
                    self.flick_timestamp[0] = time.time()
                    self.controls['left'][0] = 0
                    self.controls['left'][1] = 1
                    self.controls['right'][0] = 0
                    self.controls['right'][1] = 1
                if not self.controls[control][1] and self.controls[control][0]:
                    timestamp = time.time()
                    if (timestamp > self.flick_timestamp[0]) and (timestamp < self.flick_timestamp[0] + self.flick_pause):
                        self.controls[control][0] = 0
                        self.controls[control][1] = 1
        
        if self.controls['left'][0] and not self.controls['left'][1]:
            new_dir[0] += -1
        if self.controls['right'][0] and not self.controls['right'][1]:
            new_dir[0] += 1
        if self.controls['up'][0] and not self.controls['up'][1]:
            new_dir[1] += -1
        if self.controls['down'][0] and not self.controls['down'][1]:
            new_dir[1] += 1
    
    def check_scythe_inputs(self, player_dir):
        for control in self.controls:
            self.controls[control][1] = self.controls[control][0]
            self.controls[control][0] = 0
            for i in range(3, len(self.controls[control])):
                if not ((control == 'jump') and (self.controls[control][i] == pygame.CONTROLLER_AXIS_LEFTY)):
                    if abs(self.controls[control][2]) > i - 3:
                        if self.joystick.get_numaxes() > self.controls[control][i]:
                            if ((1 - 3 * (self.controls[control][2] < 0)) * self.joystick.get_axis(self.controls[control][i]) >= self.joystick_threshold):
                                self.controls[control][0] = 1
                                break
                    elif type(self.controls[control][i]) == type(tuple()):
                        if self.joystick.get_numhats() > 0:
                            if self.joystick.get_hat(0) == self.controls[control][i]:
                                self.controls[control][0] = 1
                                break
                    elif self.joystick.get_numbuttons() > self.controls[control][i]:
                        if self.joystick.get_button(self.controls[control][i]):
                            self.controls[control][0] = 1
                            break
            
            if (control == 'up') or (control == 'down'):
                if self.controls[control][1] and not self.controls[control][0]:
                    self.flick_timestamp[1] = time.time()
                    self.controls['up'][0] = 0
                    self.controls['up'][1] = 1
                    self.controls['down'][0] = 0
                    self.controls['down'][1] = 1
                if not self.controls[control][1] and self.controls[control][0]:
                    timestamp = time.time()
                    if (timestamp > self.flick_timestamp[1]) and (timestamp < self.flick_timestamp[1] + self.flick_pause):
                        self.controls[control][0] = 0
                        self.controls[control][1] = 1
            elif (control == 'left') or (control == 'right'):
                if self.controls[control][1] and not self.controls[control][0]:
                    self.flick_timestamp[0] = time.time()
                    self.controls['left'][0] = 0
                    self.controls['left'][1] = 1
                    self.controls['right'][0] = 0
                    self.controls['right'][1] = 1
                if not self.controls[control][1] and self.controls[control][0]:
                    timestamp = time.time()
                    if (timestamp > self.flick_timestamp[0]) and (timestamp < self.flick_timestamp[0] + self.flick_pause):
                        self.controls[control][0] = 0
                        self.controls[control][1] = 1
        
        if self.controls['left'][0]:
            player_dir[0] += -1
        if self.controls['right'][0]:
            player_dir[0] += 1
        if self.controls['up'][0]:
            player_dir[1] += -1
        if self.controls['down'][0]:
            player_dir[1] += 1

class player():
    def __init__(self, existing_players):
        self.name = 'Player ' + str(len(existing_players) + 1)
        self.base_color = 0xff0000
        self.color = 0xff0000
        self.lcolor = self.color
        self.kill_color = 0x777777
        self.invincible_color = 0x010101

        self.alive = 0
        self.lalive = 0
        
        self.gravity = 0
        self.jump_strength = 0
        self.on_ground = 0
        self.on_player = 0
        self.air_time = 0
        self.lair_time = 0

        self.pos = [0, 0]
        self.size = [0, 0]
        self.lsize = [0, 0]
        self.new_rect = [self.pos[:], self.size[:]]
        self.old_rect = [self.pos[:], self.size[:]]
        self.base_size = self.size[:]
        self.vel_terminal = [0, 0]
        self.vel_desired = [0, 0]
        self.vel_delta = [0, 0]
        self.vel = [0, 0]
        self.vel_external = []
        self.pushed = [0, 0]
        self.pushed_by = []

        self.facing = 2 * random.randint(0, 1) - 1

        self.hit_block = [0, 0]
        self.hit_player = [0, 0]

        self.squish_width = 1

        self.lpos = [0, 0]
        self.lvel = [0, 0]
        
        self.shield_health_base = 0
        self.shield_health = 0
        self.shield_regen = 0
        self.shield_broken = 0
        
        self.pushiest_player = None
        self.kills = 0
        self.wins = 0
        self.team = 0

        if len(existing_players):
            controls_length = len(existing_players[0].controls)
        else:
            controls_length = 0

        possible_controllers = len(existing_players) * controls_length
        controller_number = possible_controllers
        available_controllers = [0] * possible_controllers
        for plajer in existing_players:
            for control in plajer.controls:
                if plajer.controls[control][0] < possible_controllers:
                    available_controllers[plajer.controls[control][0]] = 1
        
        for i in range(0, len(available_controllers)):
            if available_controllers[i] == 0:
                controller_number = i
                break

        # Control: [controller # (0:), type, id, direction, last_value, value]
        # Control: [keyboard (-1), key, last_value, value]
        self.controls = {'left'   : [controller_number, 'axis', 0, -1, 0, 0],
                         'right'  : [controller_number, 'axis', 0, 1, 0, 0],
                         'up'     : [controller_number, 'axis', 1, -1, 0, 0],
                         'down'   : [controller_number, 'axis', 1, 1, 0, 0],
                         'jump'   : [controller_number, 'button', 0, 1, 0, 0],
                         'shield' : [controller_number, 'axis', 5, 1, 0, 0],
                         'ability': [controller_number, 'axis', 4, 1, 0, 0]}
    
        # Each value is the ticks remaining for that boost
        self.boosts = {'invincible' : 0,
                       'jump'       : 0,
                       'kill'       : 0,
                       'phase'      : 0,
                       'speed'      : 0}
        
        self.is_cpu = False

    def pos2(self):
        return [self.pos[0] + self.size[0], self.pos[1] + self.size[1]]

    def center(self, lvl = None):
        p = [self.pos[0] + 0.5 * self.size[0], self.pos[1] + 0.5 * self.size[1]]
        if lvl:
            if lvl.horizontal_looping:
                p[0] %= lvl.size[0]
            if lvl.vertical_looping:
                p[1] %= lvl.size[1]
        return p

    def soft_reset(self, pos, size, gravity, jump_strength, vel_terminal, vel_delta, player_shield_health_base, player_shield_regen):
        self.color = self.base_color
        self.lcolor = self.color
        self.alive = 1
        self.lalive = 1
        
        self.on_ground = 0
        self.on_player = 0
        self.air_time = 0
        self.lair_time = 0

        self.pos = pos[:]
        self.vel = [0, 0]
        self.base_size = size[:]
        self.size = size[:]
        self.lsize = size[:]
        self.surface = pygame.Surface(self.base_size)

        self.new_rect = [self.pos[:], self.size[:]]
        self.old_rect = [self.pos[:], self.size[:]]
        self.gravity = gravity
        self.jump_strength = jump_strength
        self.vel_terminal = vel_terminal[:]
        self.bouncing = 0
        self.vel_delta = vel_delta[:]
        self.vel_external = []
        self.pushed = [0, 0]
        self.pushed_by = []
        self.block_on_side = [0, 0]
        
        self.facing = 2 * random.randint(0, 1) - 1

        self.hit_block = [0, 0]
        self.hit_player = [0, 0]

        self.squish_width = 1

        self.shield_health_base = player_shield_health_base
        self.shield_health = self.shield_health_base
        self.shield_regen = player_shield_regen
        self.shield_broken = 0

        self.pushiest_player = None

        self.lpos = self.pos[:]
        self.lvel = [0, 0]
        
        self.extend_image = 0

        for control in self.controls:
            self.controls[control][-2] = 0
            self.controls[control][-1] = 0
        
        for key in self.boosts:
            self.boosts[key] = 0
        
        self.make_invincibility_surface()

        if self.is_cpu:
            self.reset_cpu_variables()




    def reset_cpu_variables(self):
        self.enemy_count = 0
        self.target = target(self, 0, 'player', 1, self)
        self.target.ticks = 1000
        self.failed_targets = []
        self.target_void = None
        self.last_void = 0

        self.average_trail_index = 0
        self.average_trail = 50 * [self.pos[:]]
        self.long_average_pos = self.pos[:]
        self.short_average_pos = self.pos[:]

        # 1 out of noise_pile times the input fails
        self.input_noise_pile = 5
        # 1 out of success_pile times the input succeeds
        self.input_success_pile = 10
        

    # [Redact] this
    def old_reset_cpu_variables(self):
        # Targets can be players, boosts, 'position', or the 'void' (the void is just a position)
        self.target = [0, 1, 'position', self.pos]
        self.target_ticks = -1
        # Entry format: [target, ticks since started following]
        # Replace old 'position' or 'void' entries
        self.past_targets = []
        #self.towards_target = 1
        #self.target_distance = 0
        #self.ltarget_distance = 0
        self.average_trail_index = 0
        self.average_trail = 50 * [self.pos[:]]
        self.long_average_pos = self.pos[:]
        self.short_average_pos = self.pos[:]

        self.input_noise_pile = 4









    def make_invincibility_surface(self):
        self.invincibility_surface = pygame.Surface(self.base_size)
        self.invincibility_surface.fill(0x010101)
        self.invincibility_surface.fill(0x000000, [[0.15 * self.base_size[0], 0.15 * self.base_size[1]], [0.7 * self.base_size[0], 0.7 * self.base_size[1]]])
        self.invincibility_surface.set_colorkey(0x000000)

    def block_collision(self, block, lvl):
        if not (self.boosts['phase'] and self.controls['ability'][-1]):
            k = check_collision_direction(self.lpos, self.size, self.vel, block.pos, block.size, lvl)
            hit_block = 0
            for i in [k, not k]:
                if self.vel[i] and block.solid:
                    if compare_wrapped(self.lpos, self.size, block.pos, block.size, lvl, not i, 0):
                        if compare_wrapped(self.pos, self.size, block.pos, block.size, lvl, not i, 0):
                            if compare_wrapped(self.pos, self.size, block.pos, block.size, lvl, i, 0):
                                if self.vel[i] >= 0:
                                    result = find_wrapped_point(block.pos[i] - self.size[i], self.size, lvl, i)
                                    self.pos[i] = result[0]
                                else:
                                    result = find_wrapped_point(block.pos[i] + block.size[i], self.size, lvl, i)
                                    self.pos[i] = result[0]
                                hit_block = 1
                                self.hit_block[i] = 1
            if hit_block:
                self.update_vel(lvl)
    
    def horizontal_block_collision(self, block, lvl):
        if block.solid:
            k = check_collision_direction(self.lpos, self.size, self.vel, block.pos, block.size, lvl)
            if k == 0:
                if compare_wrapped(self.lpos, self.size, block.pos, block.size, lvl, not k, 0):
                    if compare_wrapped(self.pos, self.size, block.pos, block.size, lvl, not k, 0):
                        if compare_wrapped(self.pos, self.size, block.pos, block.size, lvl, k, 0):
                            if self.vel[k] >= 0:
                                result = find_wrapped_point(block.pos[k] - self.size[k], self.size, lvl, k)
                                self.pos[k] = result[0]
                            else:
                                result = find_wrapped_point(block.pos[k] + block.size[k], self.size, lvl, k)
                                self.pos[k] = result[0]
                            self.hit_block[k] = 1

    # [Redact] this, it isn't being used at all
    def player_collision(self, plajer, lvl):
        k = self.vel[0] <= self.vel[1]
        hit_player = 0
        for i in [k, not k]:
            if self.vel[i] and plajer.alive:
                if compare_wrapped(self.lpos, self.size, plajer.pos, plajer.size, lvl, not i):
                    if compare_wrapped(self.pos, self.size, plajer.pos, plajer.size, lvl, i):
                        if self.vel[i] >= 0:
                            result = find_wrapped_point(plajer.pos[i] - self.size[i], self.size, lvl, i)
                            self.pos[i] = result[0]
                        else:
                            result = find_wrapped_point(plajer.pos[i] + plajer.size[i], self.size, lvl, i)
                            self.pos[i] = result[0]
                        hit_player = 1
                        self.hit_player[i] = 1
        if hit_player:
            self.update_vel(lvl)
    
    def player_vertical_collision(self, plajer, lvl):
        if not (self.boosts['phase'] and self.controls['ability'][-1]):
            hit_player = 0
            if plajer.alive or not self.alive:
                if not (plajer.boosts['phase'] and plajer.controls['ability'][-1]):
                    if check_collision_direction(self.lpos, self.size, self.vel, plajer.pos, plajer.size, lvl):
                        if compare_wrapped(self.lpos, self.size, plajer.pos, plajer.size, lvl, 0):
                            # if already inside another player look at the overlap and decide which way to push the player out
                            if self.alive and compare_wrapped(self.lpos, self.size, plajer.pos, plajer.size, lvl, 1):
                                overlap = rect_overlap(self.pos, self.size, self.vel, plajer.pos, plajer.size, lwl = lvl)
                                if abs(overlap[0]) > abs(overlap[1]):
                                    self.pos[1] += overlap[1]
                            elif compare_wrapped(self.pos, self.size, plajer.pos, plajer.size, lvl, 1):
                                if self.vel[1] >= 0:
                                    result = find_wrapped_point(plajer.pos[1] - self.size[1], self.size, lvl, 1)
                                    if self.alive or ((self.pos[1] - result[0]) < 0.4 * self.base_size[1]):
                                        self.pos[1] = result[0]
                                        hit_player = 1
                                        self.hit_player[1] = 1
                                else:
                                    if self.alive:
                                        result = find_wrapped_point(plajer.pos[1] + plajer.size[1], self.size, lvl, 1)
                                        self.pos[1] = result[0]
                                        hit_player = 1
                                        self.hit_player[1] = 1
            if hit_player:
                self.update_vel(lvl)

    def check_player_horizontal_collision(self, players, lvl, i):
        if not (self.boosts['phase'] and self.controls['ability'][-1]):
            self.vel_external = []
            if self.controls['shield'][-1] and not self.shield_broken:
                self.pushed = [1, 1]
            else:
                self.pushed = [int(self.controls['left'][-1]), int(self.controls['right'][-1])]
            self.pushed_by = []
            for ii in range(0, len(players)):
                if (i != ii):
                    plaier = players[ii]
                    if plaier.alive:
                        if not (plaier.boosts['phase'] and plaier.controls['ability'][-1]):
                            if compare_wrapped(self.pos, self.size, plaier.pos, plaier.size, lvl, 0, 1):
                                if compare_wrapped(self.pos, self.size, plaier.pos, plaier.size, lvl, 1, 1):
                                    overlap = rect_overlap(self.pos, self.size, self.vel, plaier.pos, plaier.size, plaier.vel, lwl = lvl)
                                    if has_greater_magnitude(self.vel_external, overlap[0]):
                                        self.pushiest_player = ii
                                    self.pushed_by.append(ii)
                                    self.vel_external.append(overlap[0])

    def propogate_push(self, players):
        if not (self.boosts['phase'] and self.controls['ability'][-1]):
            if self.pushed[0]:
                for i in self.pushed_by:
                    plajer = players[i]
                    if not plajer.pushed[0]:
                        plajer.pushed[0] = 1
                        plajer.propogate_push(players)
            if self.pushed[1]:
                for i in self.pushed_by:
                    plajer = players[i]
                    if not plajer.pushed[1]:
                        plajer.pushed[1] = 1
                        plajer.propogate_push(players)

    def squish(self, lvl, players, squish_delta, is_a_recurse = 0):
        if not is_a_recurse:
            self.extend_image = 0
        if not (self.boosts['phase'] and self.controls['ability'][-1]):
            if (is_a_recurse <= 1) and (not (self.controls['shield'][-1] and not self.shield_broken)):
                smaller_squisher_pos = -self.size[0]
                bigger_squisher_pos = lvl.size[0] + self.size[0]
                block_on_side = [0, 0]
                for thing in lvl.blocks + players:
                    is_player = (type(thing) == type(self))
                    if (self.pos == thing.pos) and (self.size == thing.size):
                        continue
                    if is_player:
                        if not thing.alive:
                            continue
                        if thing.boosts['phase'] and thing.controls['ability'][-1]:
                            continue
                    else:
                        if not thing.solid:
                            continue
                    if is_a_recurse == 1:
                        multiplier = 0
                    elif self.squish_width + squish_delta > 1:
                        multiplier = 1 - self.squish_width
                    else:
                        multiplier = squish_delta
                    p1 = [self.pos[0] - 0.5 * self.base_size[0] * multiplier, self.pos[1]]
                    s1 = [self.size[0] + self.base_size[0] * multiplier, self.size[1]]
                    if compare_wrapped(p1, s1, thing.pos, thing.size, lvl, 0, 1):
                        if compare_wrapped(p1, s1, thing.pos, thing.size, lvl, 1, 0):
                            if lvl.horizontal_looping:
                                if (((p1[0] + 0.5 * s1[0]) - (thing.pos[0] + 0.5 * thing.size[0]) + 0.5 * lvl.size[0]) % lvl.size[0] - 0.5 * lvl.size[0]) >= 0:
                                    if (thing.pos[0] + thing.size[0]) % lvl.size[0] > smaller_squisher_pos:
                                        smaller_squisher_pos = (thing.pos[0] + thing.size[0]) % lvl.size[0]
                                        block_on_side[0] = not is_player
                                    elif (thing.pos[0] + thing.size[0]) % lvl.size[0] == smaller_squisher_pos:
                                        if not is_player:
                                            block_on_side[0] = 1
                                elif thing.pos[0] % lvl.size[0] < bigger_squisher_pos:
                                    bigger_squisher_pos = thing.pos[0] % lvl.size[0]
                                    block_on_side[1] = not is_player
                                elif thing.pos[0] % lvl.size[0] == bigger_squisher_pos:
                                    if not is_player:
                                        block_on_side[1] = 1
                            else:
                                if (p1[0] + 0.5 * s1[0]) - (thing.pos[0] + 0.5 * thing.size[0]) >= 0:
                                    if thing.pos[0] + thing.size[0] > smaller_squisher_pos:
                                        smaller_squisher_pos = thing.pos[0] + thing.size[0]
                                        block_on_side[0] = not is_player
                                    elif thing.pos[0] + thing.size[0] == smaller_squisher_pos:
                                        if not is_player:
                                            block_on_side[0] = 1
                                elif thing.pos[0] < bigger_squisher_pos:
                                    bigger_squisher_pos = thing.pos[0]
                                    block_on_side[1] = not is_player
                                elif thing.pos[0] == bigger_squisher_pos:
                                    if not is_player:
                                        block_on_side[1] = 1
                if not lvl.horizontal_looping:
                    if smaller_squisher_pos <= -self.size[0] * lvl.side_wall_depth * 0.01:
                        if self.pos[0] <= -self.size[0] * lvl.side_wall_depth * 0.01:
                            smaller_squisher_pos = -self.size[0] * lvl.side_wall_depth * 0.01
                            block_on_side[0] = 1
                    if bigger_squisher_pos >= lvl.size[0] + self.size[0] * lvl.side_wall_depth * 0.01:
                        if self.pos[0] >= lvl.size[0] + self.size[0] * (lvl.side_wall_depth * 0.01 - 1):
                            bigger_squisher_pos = lvl.size[0] + self.size[0] * lvl.side_wall_depth * 0.01
                            block_on_side[1] = 1
                if (smaller_squisher_pos == -self.size[0]) and (bigger_squisher_pos == lvl.size[0] + self.size[0]):
                    # expand appropriately when there is noone on either side
                    self.size[0] = s1[0]
                    self.pos[0] = p1[0]
                elif smaller_squisher_pos == -self.size[0]:
                    # expand appropriately when there is one side
                    if block_on_side[1]:
                        self.extend_image = 1
                    self.size[0] = s1[0]
                    if lvl.horizontal_looping:
                        self.pos[0] = (bigger_squisher_pos - self.size[0]) % lvl.size[0]
                    else:
                        self.pos[0] = bigger_squisher_pos - self.size[0]
                    self.squish(lvl, players, squish_delta, is_a_recurse + 1)
                elif bigger_squisher_pos == lvl.size[0] + self.size[0]:
                    # expand appropriately when there is one side
                    self.size[0] = s1[0]
                    self.pos[0] = smaller_squisher_pos
                    self.squish(lvl, players, squish_delta, is_a_recurse + 1)
                elif block_on_side != [0, 0] or self.pushed == [1, 1]:
                    # squish appropriately sometimes when there is a thing on both sides
                    if block_on_side[1]:
                        self.extend_image = 1
                    self.pos[0] = smaller_squisher_pos
                    if lvl.horizontal_looping:
                        self.size[0] = (bigger_squisher_pos - smaller_squisher_pos + 0.5 * lvl.size[0]) % lvl.size[0] - 0.5 * lvl.size[0]
                    else:
                        self.size[0] = bigger_squisher_pos - smaller_squisher_pos
                self.size[0] = abs(self.size[0])
                if self.base_size[0] != 0:
                    if self.size[0] > self.base_size[0]:
                        self.size[0] = self.base_size[0]
                    self.squish_width = self.size[0] / self.base_size[0]
                else:
                    self.squish_width = 0
                if self.squish_width > 1:
                    self.squish_width = 1
                if self.squish_width == 1:
                    self.extend_image = 0
                self.block_on_side = block_on_side

    def expand(self, lvl, squish_delta, is_a_recurse = 0):
        if not is_a_recurse:
            self.extend_image = 0
        if not (self.boosts['phase'] and self.controls['ability'][-1]):
            if (is_a_recurse <= 1) and (not (self.controls['shield'][-1] and not self.shield_broken)):
                smaller_squisher_pos = -self.size[0]
                bigger_squisher_pos = lvl.size[0] + self.size[0]
                block_on_side = [0, 0]
                for block in lvl.blocks:
                    if not block.solid:
                        continue
                    if is_a_recurse == 1:
                        multiplier = 0
                    elif self.squish_width + squish_delta > 1:
                        multiplier = 1 - self.squish_width
                    else:
                        multiplier = squish_delta
                    p1 = [self.pos[0] - 0.5 * self.base_size[0] * multiplier, self.pos[1]]
                    s1 = [self.size[0] + self.base_size[0] * multiplier, self.size[1]]
                    if compare_wrapped(p1, s1, block.pos, block.size, lvl, 0, 1):
                        if compare_wrapped(p1, s1, block.pos, block.size, lvl, 1, 0):
                            if lvl.horizontal_looping:
                                if (((p1[0] + 0.5 * s1[0]) - (block.pos[0] + 0.5 * block.size[0]) + 0.5 * lvl.size[0]) % lvl.size[0] - 0.5 * lvl.size[0]) >= 0:
                                    if (block.pos[0] + block.size[0]) % lvl.size[0] > smaller_squisher_pos:
                                        smaller_squisher_pos = (block.pos[0] + block.size[0]) % lvl.size[0]
                                        block_on_side[0] = 1
                                elif block.pos[0] % lvl.size[0] < bigger_squisher_pos:
                                    bigger_squisher_pos = block.pos[0] % lvl.size[0]
                                    block_on_side[1] = 1
                            else:
                                if (p1[0] + 0.5 * s1[0]) - (block.pos[0] + 0.5 * block.size[0]) >= 0:
                                    if block.pos[0] + block.size[0] > smaller_squisher_pos:
                                        smaller_squisher_pos = block.pos[0] + block.size[0]
                                        block_on_side[0] = 1
                                elif block.pos[0] < bigger_squisher_pos:
                                    bigger_squisher_pos = block.pos[0]
                                    block_on_side[1] = 1
                if not lvl.horizontal_looping:
                    if smaller_squisher_pos <= -self.size[0] * lvl.side_wall_depth * 0.01:
                        if self.pos[0] <= -self.size[0] * lvl.side_wall_depth * 0.01:
                            smaller_squisher_pos = -self.size[0] * lvl.side_wall_depth * 0.01
                            block_on_side[0] = 1
                    if bigger_squisher_pos >= lvl.size[0] + self.size[0] * lvl.side_wall_depth * 0.01:
                        if self.pos[0] >= lvl.size[0] + self.size[0] * (lvl.side_wall_depth * 0.01 - 1):
                            bigger_squisher_pos = lvl.size[0] + self.size[0] * lvl.side_wall_depth * 0.01
                            block_on_side[1] = 1
                if (smaller_squisher_pos == -self.size[0]) and (bigger_squisher_pos == lvl.size[0] + self.size[0]):
                    # expand appropriately when there is noone on either side
                    self.size[0] = s1[0]
                    self.pos[0] = p1[0]
                elif smaller_squisher_pos == -self.size[0]:
                    # expand appropriately when there is one side
                    if block_on_side[1]:
                        self.extend_image = 1
                    self.size[0] = s1[0]
                    if lvl.horizontal_looping:
                        self.pos[0] = (bigger_squisher_pos - self.size[0]) % lvl.size[0]
                    else:
                        self.pos[0] = bigger_squisher_pos - self.size[0]
                    self.expand(lvl, squish_delta, is_a_recurse + 1)
                elif bigger_squisher_pos == lvl.size[0] + self.size[0]:
                    # expand appropriately when there is one side
                    self.size[0] = s1[0]
                    self.pos[0] = smaller_squisher_pos
                    self.expand(lvl, squish_delta, is_a_recurse + 1)
                elif block_on_side != [0, 0] or self.pushed == [1, 1]:
                    # expand appropriately sometimes when there is a block on both sides
                    if block_on_side[1]:
                        self.extend_image = 1
                    self.pos[0] = smaller_squisher_pos
                    if lvl.horizontal_looping:
                        self.size[0] = (bigger_squisher_pos - smaller_squisher_pos + 0.5 * lvl.size[0]) % lvl.size[0] - 0.5 * lvl.size[0]
                    else:
                        self.size[0] = bigger_squisher_pos - smaller_squisher_pos
                self.size[0] = abs(self.size[0])
                if self.base_size[0] != 0:
                    if self.size[0] > self.base_size[0]:
                        self.size[0] = self.base_size[0]
                    self.squish_width = self.size[0] / self.base_size[0]
                else:
                    self.squish_width = 0
                if self.squish_width > 1:
                    self.squish_width = 1
                if self.squish_width == 1:
                    self.extend_image = 0
                self.block_on_side = block_on_side

    def save_old_rect(self):
        self.old_rect = [self.pos[:], self.size[:]]
    
    def load_old_rect(self):
        self.pos = self.old_rect[0][:]
        self.size = self.old_rect[1][:]
    
    def save_new_rect(self):
        self.new_rect = [self.pos[:], self.size[:]]
    
    def load_new_rect(self):
        self.pos = self.new_rect[0][:]
        self.size = self.new_rect[1][:]

    def update_vel(self, lvl):
        # This assumes any movement larger that half the screen was a screen wrap
        self.vel = [self.pos[0] - self.lpos[0], self.pos[1] - self.lpos[1]]
        if lvl.horizontal_looping:
            if abs(self.vel[0]) > lvl.size[0] / 2:
                self.vel[0] = (self.vel[0] + lvl.size[0] / 2) % lvl.size[0] - lvl.size[0] / 2
        if lvl.vertical_looping:
            if abs(self.vel[1]) > lvl.size[1] / 2:
                self.vel[1] = (self.vel[1] + lvl.size[1] / 2) % lvl.size[1] - lvl.size[1] / 2

    def check_squished(self, lvl, kill_width, players, death_animations):
        if not self.boosts['invincible']:
            if not (self.boosts['phase'] and self.controls['ability'][-1]):
                if self.squish_width <= kill_width:
                    self.alive = 0
                    death_animations.append(death_animation(self.center(lvl), self.base_size))
                    if self.pushiest_player != None:
                        players[self.pushiest_player].kills += 1

    def check_kill(self, lvl, players, kill_width, shield_color, player_index, death_animations):
        if not (self.boosts['phase'] and self.controls['ability'][-1]):
            for i in range(0, len(players)):
                if i != player_index:
                    plajer = players[i]
                    if not plajer.boosts['invincible']:
                        if plajer.alive:
                            if not (plajer.boosts['phase'] and plajer.controls['ability'][-1]):
                                if plajer.color != shield_color:
                                    if compare_wrapped([self.pos[0] + self.size[0] * (1 - kill_width) / 2, 0], [self.size[0] * kill_width, 0], [plajer.pos[0] + plajer.size[0] * (1 - kill_width) / 2, 0], [plajer.size[0] * kill_width, 0], lvl, 0, 1):
                                        if compare_wrapped(self.pos, self.size, plajer.pos, [0, plajer.size[1] - self.size[1]], lvl, 1, 1):
                                            plajer.alive = 0
                                            death_animations.append(death_animation(plajer.center(lvl), plajer.base_size))
                                            self.kills += 1
                                if self.boosts['kill'] and not plajer.boosts['kill']:
                                    if compare_wrapped(self.pos, self.size, plajer.pos, plajer.size, lvl, 0, 1):
                                        if compare_wrapped(self.pos, self.size, plajer.pos, plajer.size, lvl, 1, 1):
                                            plajer.alive = 0
                                            death_animations.append(death_animation(plajer.center(lvl), plajer.base_size))
                                            self.kills += 1

    def ability_death(self, plajer, shield_color, death_animations, lvl):
        if not (self.boosts['phase'] and self.controls['ability'][-1]):
            if not self.boosts['invincible']:
                if self.shield_broken or not (self.color == shield_color):
                    self.alive = 0
                    death_animations.append(death_animation(self.center(lvl), self.base_size))
                    plajer.kills += 1

    def check_ground(self, lvl, players, player_index):
        self.lair_time = self.air_time
        if not self.on_ground and not self.on_player:
            self.air_time += 1
        elif self.vel[1] <= 0:
            self.air_time = 0
        self.on_ground = 0
        for block in lvl.blocks:
            if block.solid:
                if compare_wrapped(self.pos, self.size, block.pos, block.size, lvl, 0, 1):
                    if compare_wrapped(self.pos, self.size, block.pos, [0, block.size[1] - self.size[1]], lvl, 1, 1):
                        self.on_ground = 1
                        break
        self.on_player = 0
        for i in range(0, len(players)):
            if i != player_index:
                plajer = players[i]
                if plajer.alive or (not self.alive):
                    if not (plajer.boosts['phase'] and plajer.controls['ability'][-1]):
                        if compare_wrapped(self.pos, self.size, plajer.pos, plajer.size, lvl, 0, 1):
                            if compare_wrapped(self.pos, self.size, plajer.pos, [0, plajer.size[1] - self.size[1]], lvl, 1, 1):
                                self.on_player = 1
                                break

    def display(self, lvl, su_rects, team_colors, do_teams):
        if self.extend_image:
            real_size = self.size[:]
            self.size[0] += 1
        self.surface.fill(self.color)
        if do_teams:
            if self.team > 0:
                color = team_colors[self.team - 1]
            else:
                color = 0x443333
            p = [0.6 * self.base_size[0], 0]
            s = [0.3 * self.base_size[0], self.base_size[1]]
            pygame.draw.rect(self.surface, color, [p, s])
        if (self.name.lower() == 'yoshi') and (self.base_color == 0x00aa00):
            if not self.shield_broken and self.controls['shield'][-1]:
                self.surface.fill(0xcecece)
                p = [0, 0.15 * self.base_size[1]]
                s = [0.4 * self.base_size[0], 0.4 * self.base_size[1]]
                pygame.draw.rect(self.surface, 0x00aa00, [p, s])
                p = [0.6 * self.base_size[0], 0]
                s = [0.4 * self.base_size[0], 0.3 * self.base_size[1]]
                pygame.draw.rect(self.surface, 0x00aa00, [p, s])
                p = [0.5 * self.base_size[0], 0.45 * self.base_size[1]]
                s = [0.5 * self.base_size[0], 0.5 * self.base_size[1]]
                pygame.draw.rect(self.surface, 0x00aa00, [p, s])
        if self.boosts['kill']:
            pygame.draw.rect(self.surface, self.kill_color, [[0, 0.2 * self.base_size[1]], [self.base_size[0], 0.2 * self.base_size[1]]])
        if self.boosts['invincible']:
            self.surface.blit(self.invincibility_surface, [0, 0])
        if (self.name.lower() == 'game and watch') and (self.base_color == 0x000000):
            real_pos = self.pos[:]
            real_lpos = self.lpos[:]
            self.lpos = self.gaw_llpos[:]
            m = 0.75
            for i in range(0, 2):
                if self.gaw_lpos[i] == real_pos[i]:
                    if self.gaw_counter[i] < 5:
                        self.gaw_counter[i] += 1
                else:
                    self.gaw_counter[i] = 0
                if self.gaw_counter[i] >= 5:
                    self.gaw_adjustment[i] = self.pos[i] % (m * self.base_size[i])
            self.gaw_lpos = self.pos[:]
            if self.base_size[0] != 0:
                self.pos[0] = m * self.base_size[0] * (self.pos[0] // (m * self.base_size[0])) + self.gaw_adjustment[0]
            if self.base_size[1] != 0:
                self.pos[1] = m * self.base_size[1] * (self.pos[1] // (m * self.base_size[1])) + self.gaw_adjustment[1]
            self.gaw_llpos = self.pos[:]
        if not self.alive:
            self.surface.set_alpha(40)
        lvl.surface.blit(pygame.transform.scale(self.surface, self.size), self.pos)
        if lvl.horizontal_looping:
            pos = [self.pos[0] - lvl.size[0], self.pos[1]]
            lvl.surface.blit(pygame.transform.scale(self.surface, self.size), pos)
        if lvl.vertical_looping:
            pos = [self.pos[0], self.pos[1] - lvl.size[1]]
            lvl.surface.blit(pygame.transform.scale(self.surface, self.size), pos)
        if lvl.horizontal_looping and lvl.vertical_looping:
            pos = [self.pos[0] - lvl.size[0], self.pos[1] - lvl.size[1]]
            lvl.surface.blit(pygame.transform.scale(self.surface, self.size), pos)
        if self.extend_image:    
            self.size = real_size[:]
        
        self.append_su_rects(lvl, su_rects)
        
        if (self.name.lower() == 'game and watch') and (self.base_color == 0x000000):
            self.pos = real_pos[:]
            self.lpos = real_lpos[:]
    
    def append_su_rects(self, lvl, su_rects):
        if (self.pos != self.lpos) or (self.size != self.lsize) or (self.color != self.lcolor) or (not self.alive and self.lalive):
            su_rects.append([self.lpos, self.lsize])
            su_rects.append([self.pos, self.size])
            if lvl.horizontal_looping:
                lp = [self.lpos[0] - lvl.size[0], self.lpos[1]]
                p = [self.pos[0] - lvl.size[0], self.pos[1]]
                su_rects.append([lp, self.lsize])
                su_rects.append([p, self.size])
            if lvl.vertical_looping:
                lp = [self.lpos[0], self.lpos[1] - lvl.size[1]]
                p = [self.pos[0], self.pos[1] - lvl.size[1]]
                su_rects.append([lp, self.lsize])
                su_rects.append([p, self.size])
            if lvl.horizontal_looping and lvl.vertical_looping:
                lp = [self.lpos[0] - lvl.size[0], self.lpos[1] - lvl.size[1]]
                p = [self.pos[0] - lvl.size[0], self.pos[1] - lvl.size[1]]
                su_rects.append([lp, self.lsize])
                su_rects.append([p, self.size])

    def spawn_arrow(self, lvl, image):
        if self.shield_broken or not self.controls['shield'][-1]:
            if self.arrow_counter <= 0:
                p = self.center(lvl)
                s = 0.8 * self.base_size[0]
                v = [self.facing * 4 * self.vel_terminal[0], -1 * self.vel_terminal[0] + 1 * self.vel[1]]
                g = 0.02 * self.gravity
                self.arrows.append(arrow(p, s, v, g, image))
                self.arrow_counter = self.arrow_counter_reset
                return 1
        return 0
    
    def spawn_fire(self, lvl, image):
        if self.shield_broken or not self.controls['shield'][-1]:
            if self.fire_counter <= 0:
                p = self.center(lvl)
                s = 0.5 * self.base_size[0]
                v = [self.facing * 2 * self.vel_terminal[0], 0]
                self.fires.append(fire(p, s, v, image, self.fire_life))
                self.fire_counter = self.fire_counter_reset
                return 1
        return 0
    
    def spawn_zap(self, images, colorkey):
        if self.shield_broken or not self.controls['shield'][-1]:
            if self.zap_counter <= 0:
                p = self.pos
                s = 0.4 * self.base_size[0]
                self.zaps.append(zap(p, s, self.facing, images, colorkey))
                self.zap_counter = self.zap_counter_reset
                return 1
        return 0

class target():
    def __init__(self, parent, weight, tipe, din, target, lvl = None):
        self.parent = parent
        self.weight = weight
        self.ticks = 0
        self.type = tipe
        self.dir = din
        self.target = target
        if self.type == 'boost':
            self.pos = self.target[0]
        elif self.type == 'player':
            self.pos = self.target.center(lvl)
        else:
            self.pos = target
        self.satisfied = 0
    
    def check_satisfied(self, lvl, boosts):
        if not self.satisfied:
            # Boost is gone
            if self.type == 'boost':
                self.satisfied = not boosts.count(self.target)
            # Player has died
            elif self.type == 'player':
                self.satisfied = not self.target.alive
            # Position reached
            else:
                self.satisfied = in_rect(self.pos, self.parent.pos, self.parent.size, lvl)
        return self.satisfied
    
class arrow():
    def __init__(self, pos, size, vel, gravity, image):
        self.size = [size, 0.3 * size]
        self.pos = [pos[0] - 0.5 * self.size[0], pos[1] - 0.5 * self.size[1]]
        self.vel = vel[:]
        self.gravity = gravity
        self.life = 150
        self.image = pygame.transform.scale(image, self.size)
        if self.vel[0] < 0:
            self.image = pygame.transform.flip(self.image, 1, 0)

class fire():
    def __init__(self, pos, size, vel, image, life):
        self.size = [size, size]
        self.pos = [pos[0] - 0.5 * self.size[0], pos[1] - 0.5 * self.size[1]]
        self.vel = vel[:]
        self.life = life
        self.image = pygame.transform.scale(image, self.size)
        if self.vel[0] < 0:
            self.image = pygame.transform.flip(self.image, 1, 0)

class zap():
    def __init__(self, pos, size, facing, images, colorkey):
        self.pos = pos[:]
        self.lpos = pos[:]
        self.size = [4 * size, size]
        self.life = 25
        self.image_no = 0
        self.sprites = []
        self.facing = facing
        for image in images:
            self.sprites.append(pygame.transform.scale(image, [size, size]))
        self.images = []
        for sprite in self.sprites:
            image = pygame.Surface(self.size)
            image.fill(colorkey)
            image.set_colorkey(colorkey)
            image.blit(sprite, [0, 0])
            image.blit(sprite, [size, 0])
            image.blit(sprite, [2 * size, 0])
            image.fill(sprite.get_at([10, 10]), [[3 * size, 0], [size, size]])
            if self.facing < 0:
                image = pygame.transform.flip(image, 1, 0)
            self.images.append(image)

    def get_image(self):
        image = self.images[self.image_no]
        self.image_no = (self.image_no + 1) % len(self.images)
        return image

class level():
    def __init__(self, file, name):
        self.file = file
        self.name = name
        self.size = [0, 0]
        self.background_color = 0
        self.player_size = [0, 0]
        self.player_gravity = 0
        self.player_jump_strength = 0
        self.player_vel_terminal = [0, 0]
        self.player_vel_delta = [0, 0]
        self.vertical_looping = 0
        self.horizontal_looping = 0
        self.side_wall_depth = 0

        self.player_shield_health_base = 0
        self.player_shield_regen = 0
        
        self.blocks = []
        self.blocks_history = []
        self.player_poses = []
        self.player_poses_history = []

        objekt_type = 0
        objekt = 0
        for line in self.file:
            no_spaces_line = line.replace(' ', '')
            no_comment_line = no_spaces_line.split('#')[0]
            no_return_line = no_comment_line.replace('\n', '')
            split_line = no_return_line.split('=')
            properky = split_line[0]
            value = split_line[-1]
            if properky == 'level':
                if objekt_type == 'block':
                    self.blocks.append(objekt)
                objekt_type = 'level'
            elif properky == 'player_pos':
                self.player_poses.append(findxy(value, is_int = 1))
            elif properky == 'block':
                if objekt_type == 'block':
                    self.blocks.append(objekt)
                objekt_type = 'block'
                objekt = level_block()
            if objekt_type == 'level':
                if properky == 'size':
                    size = findxy(value)
                    self.size = [int(size[0]), int(size[1])]
                    self.rescale()
                elif properky == 'background_color':
                    self.background_color = int(value, 16)
                elif properky == 'player_size':
                    self.player_size = findxy(value)
                elif properky == 'player_gravity':
                    self.player_gravity = float(value)
                elif properky == 'player_jump_strength':
                    self.player_jump_strength = float(value)
                elif properky == 'player_vel_terminal':
                    self.player_vel_terminal = findxy(value)
                elif properky == 'player_vel_delta':
                    self.player_vel_delta = findxy(value)
                elif properky == 'vertical_looping':
                    self.vertical_looping = (value.lower() == 'true') or (value == '1')
                elif properky == 'horizontal_looping':
                    self.horizontal_looping = (value.lower() == 'true') or (value == '1')
                elif properky == 'side_wall_depth':
                    self.side_wall_depth = float(value)
                elif properky == 'player_shield_health_base':
                    self.player_shield_health_base = float(value)
                elif properky == 'player_shield_regen':
                    self.player_shield_regen = float(value)
            elif objekt_type == 'block':
                if properky == 'size':
                    objekt.size = findxy(value, is_int = 1)
                elif properky == 'pos':
                    objekt.pos = findxy(value, is_int = 1)
                elif properky == 'color':
                    objekt.color = int(value, 16)
                elif properky == 'solid':
                    objekt.solid = (value.lower() == 'true') or (value == '1')
        if objekt_type == 'block':
            self.blocks.append(objekt)

        self.surface = pygame.Surface(self.size)
        self.render_block_surfaces()
        self.render_thumbnail()

    def rescale(self, refrence = [1920, 1080]):
        refrence[0] += (refrence[0] == 0)
        refrence[1] += (refrence[1] == 0)
        self.size[0] += (self.size[0] == 0)
        self.size[1] += (self.size[1] == 0)
        self.scale = [self.size[0] / refrence[0], self.size[1] / refrence[1]]
        self.inv_scale = [1 / self.scale[0], 1 / self.scale[1]]

    def duplicate(self, i):
        new_blocks = []
        old_blocks = self.blocks[:]
        for block in old_blocks:
            new_block = level_block()
            new_block.copy_from(block)
            new_block.pos[i] = self.size[i] - new_block.pos[i] - new_block.size[i]
            already_exists = 0
            for blokk in old_blocks:
                if new_block.size == blokk.size:
                    if new_block.pos == blokk.pos:
                        if new_block.color == blokk.color:
                            if new_block.solid == blokk.solid:
                                already_exists = 1
                                break
            if not already_exists:
                self.blocks.append(new_block)
                new_blocks.append(new_block)
        
        new_player_poses = []
        old_player_poses = self.player_poses[:]
        for player_pos in old_player_poses:
            new_player_pos = player_pos[:]
            new_player_pos[i] = self.size[i] - new_player_pos[i] - self.player_size[i]
            already_exists = 0
            for plajer_pos in old_player_poses:
                if new_player_pos == plajer_pos:
                    already_exists = 1
            if not already_exists:
                self.player_poses.append(new_player_pos)
                new_player_poses.append(new_player_pos)
        
        if len(new_blocks) or len(new_player_poses):
            self.blocks_history.append(new_blocks)
            self.player_poses_history.append(new_player_poses)
        
        self.render_block_surfaces()

    def undo(self):
        if len(self.blocks_history):
            lem = len(self.blocks)
            for i in range(0, lem):
                h = lem - i - 1
                for block in self.blocks_history[-1]:
                    if self.blocks[h].size == block.size:
                        if self.blocks[h].pos == block.pos:
                            if self.blocks[h].color == block.color:
                                if self.blocks[h].solid == block.solid:
                                    self.blocks.pop(h)
                                    break
            self.blocks_history.pop()
        if len(self.player_poses_history):
            lem = len(self.player_poses)
            for i in range(0, lem):
                h = lem - i - 1
                for player_pos in self.player_poses_history[-1]:
                    if self.player_poses[h] == player_pos:
                        self.player_poses.pop(h)
                        break
            self.player_poses_history.pop()
        
        self.render_block_surfaces()

    def render_block_surfaces(self):
        # Create unsolid block surface
        self.surface_unsolid = pygame.Surface(self.size)
        self.surface_unsolid.set_colorkey(0x010101)
        self.surface_unsolid.fill(0x010101)
        for block in self.blocks:
            if not block.solid:
                pygame.draw.rect(self.surface_unsolid, block.color, [block.pos, block.size])
                if self.horizontal_looping:
                    if block.pos[0] < 0:
                        p = [block.pos[0] + self.size[0], block.pos[1]]
                        pygame.draw.rect(self.surface_unsolid, block.color, [p, block.size])
                    if block.pos[0] + block.size[0] > self.size[0]:
                        p = [block.pos[0] - self.size[0], block.pos[1]]
                        pygame.draw.rect(self.surface_unsolid, block.color, [p, block.size])
                if self.vertical_looping:
                    if block.pos[1] < 0:
                        p = [block.pos[0], block.pos[1] + self.size[1]]
                        pygame.draw.rect(self.surface_unsolid, block.color, [p, block.size])
                    if block.pos[1] + block.size[1] > self.size[1]:
                        p = [block.pos[0], block.pos[1] - self.size[1]]
                        pygame.draw.rect(self.surface_unsolid, block.color, [p, block.size])
                if self.vertical_looping and self.horizontal_looping:
                    if block.pos[0] < 0:
                        if block.pos[1] < 0:
                            p = [block.pos[0] + self.size[0], block.pos[1] + self.size[1]]
                            pygame.draw.rect(self.surface_unsolid, block.color, [p, block.size])
                        if block.pos[1] + block.size[1] > self.size[1]:
                            p = [block.pos[0] + self.size[0], block.pos[1] - self.size[1]]
                            pygame.draw.rect(self.surface_unsolid, block.color, [p, block.size])
                    if block.pos[0] + block.size[0] > self.size[0]:
                        if block.pos[1] < 0:
                            p = [block.pos[0] - self.size[0], block.pos[1] + self.size[1]]
                            pygame.draw.rect(self.surface_unsolid, block.color, [p, block.size])
                        if block.pos[1] + block.size[1] > self.size[1]:
                            p = [block.pos[0] - self.size[0], block.pos[1] - self.size[1]]
                            pygame.draw.rect(self.surface_unsolid, block.color, [p, block.size])
        # Create solid block surface
        self.surface_solid = pygame.Surface(self.size)
        self.surface_solid.set_colorkey(0x010101)
        self.surface_solid.fill(0x010101)
        for block in self.blocks:
            if block.solid:
                pygame.draw.rect(self.surface_solid, block.color, [block.pos, block.size])
                if self.horizontal_looping:
                    if block.pos[0] < 0:
                        p = [block.pos[0] + self.size[0], block.pos[1]]
                        pygame.draw.rect(self.surface_solid, block.color, [p, block.size])
                    if block.pos[0] + block.size[0] > self.size[0]:
                        p = [block.pos[0] - self.size[0], block.pos[1]]
                        pygame.draw.rect(self.surface_solid, block.color, [p, block.size])
                if self.vertical_looping:
                    if block.pos[1] < 0:
                        p = [block.pos[0], block.pos[1] + self.size[1]]
                        pygame.draw.rect(self.surface_solid, block.color, [p, block.size])
                    if block.pos[1] + block.size[1] > self.size[1]:
                        p = [block.pos[0], block.pos[1] - self.size[1]]
                        pygame.draw.rect(self.surface_solid, block.color, [p, block.size])
                if self.vertical_looping and self.horizontal_looping:
                    if block.pos[0] < 0:
                        if block.pos[1] < 0:
                            p = [block.pos[0] + self.size[0], block.pos[1] + self.size[1]]
                            pygame.draw.rect(self.surface_solid, block.color, [p, block.size])
                        if block.pos[1] + block.size[1] > self.size[1]:
                            p = [block.pos[0] + self.size[0], block.pos[1] - self.size[1]]
                            pygame.draw.rect(self.surface_solid, block.color, [p, block.size])
                    if block.pos[0] + block.size[0] > self.size[0]:
                        if block.pos[1] < 0:
                            p = [block.pos[0] - self.size[0], block.pos[1] + self.size[1]]
                            pygame.draw.rect(self.surface_solid, block.color, [p, block.size])
                        if block.pos[1] + block.size[1] > self.size[1]:
                            p = [block.pos[0] - self.size[0], block.pos[1] - self.size[1]]
                            pygame.draw.rect(self.surface_solid, block.color, [p, block.size])

    def render_thumbnail(self):
        self.thumbnail = pygame.Surface(self.size)
        self.thumbnail.fill(self.background_color)

        self.thumbnail.blit(self.surface_unsolid, [0, 0])
        self.thumbnail.blit(self.surface_solid, [0, 0])

        for block in self.blocks:
            pygame.draw.rect(self.thumbnail, block.color, [block.pos, block.size])

    def export_level_file(self):
        cwd = os.getcwd()
        level_directory = os.path.join(cwd, 'levels')
        file = open(os.path.join(level_directory, self.name + '.txt'), mode = 'w', encoding = 'utf-8')
        
        file.write('level\n')
        file.write('    size = ' + str(self.size) + '\n')
        file.write('    background_color = 0x' + hex(self.background_color)[2:].rjust(6, '0') + '\n')
        file.write('    player_size = ' + str(self.player_size) + '\n')
        file.write('    player_gravity = ' + str(self.player_gravity) + '\n')
        file.write('    player_jump_strength = ' + str(self.player_jump_strength) + '\n')
        file.write('    player_vel_terminal = ' + str(self.player_vel_terminal) + '\n')
        file.write('    player_vel_delta = ' + str(self.player_vel_delta) + '\n')
        file.write('    vertical_looping = ' + 'true' * (self.vertical_looping) + 'false' * (not self.vertical_looping) + '\n')
        file.write('    horizontal_looping = ' + 'true' * (self.horizontal_looping) + 'false' * (not self.horizontal_looping) + '\n')
        file.write('    side_wall_depth = ' + str(self.side_wall_depth) + '\n')
        file.write('    player_shield_health_base = ' + str(self.player_shield_health_base) + '\n')
        file.write('    player_shield_regen = ' + str(self.player_shield_regen))

        for i in range(0, len(self.player_poses)):
            if i == 0:
                file.write('\n')
            file.write('\n')
            file.write('player_pos = ' + str(self.player_poses[i]))

        for block in self.blocks:
            file.write('\n\n')
            file.write('block\n')
            file.write('    size = ' + str(block.size) + '\n')
            file.write('    pos = ' + str(block.pos) + '\n')
            file.write('    color = 0x' + hex(block.color)[2:].rjust(6, '0') + '\n')
            file.write('    solid = ' + 'true' * (block.solid) + 'false' * (not block.solid))

        file.close()

class level_block():
    def __init__(self):
        self.size = [0, 0]
        self.pos = [0, 0]
        self.color = 0
        self.solid = 0
    
    def copy_from(self, target):
        self.size = target.size[:]
        self.pos = target.pos[:]
        self.color = target.color
        self.solid = target.solid

class death_animation():
    def __init__(self, pos, size, life = 10, colors = [0xffffff, 0x000000, 0x000000]):
        self.pos = pos[:]
        self.size = size[:]
        self.life = life
        self.colors = colors
        self.color_count = len(self.colors)
        self.color = self.colors[self.life % self.color_count]

        self.orects = [[pos[:], [0, 0]], [pos[:], [0, 0]], [pos[:], [0, 0]], [pos[:], [0, 0]]]
        self.rects = self.orects[:]
        self.lrects = self.orects[:]
        self.delta = [0.5 * size[0] / self.life, 0.5 * size[1] / self.life]
    
    def get_rects(self):
        self.lrects = self.rects[:]
        new_rects = []
        for i in range(0, 2):
            for ii in range(0, 2):
                r = self.orects[2 * i + ii]
                p = r[0]
                p[0] += 0.7 * (2 * i * self.delta[0] - self.delta[0])
                p[1] += 0.7 * (2 * ii * self.delta[1] - self.delta[1])
                s = r[1]
                s[0] += self.delta[0]
                s[1] += self.delta[1]
                r = [p, s]
                new_rects.append([[p[0] - 0.5 * s[0], p[1] - 0.5 * s[1]], s])
        self.life += -1
        self.color = self.colors[self.life % self.color_count]
        self.rects = new_rects
        return self.rects

class sound():
    def __init__(self, cwd, volume):
        self.sound_effect_directory = os.path.join(cwd, 'sound effects')
        self.music_directory = os.path.join(cwd, 'music')
        self.load_sounds()
        self.set_volume(volume)

    def load_sounds(self):
        self.sounds = {}
        for file_name in os.listdir(self.sound_effect_directory):
            self.sounds[file_name.replace('.wav', '')] = pygame.mixer.Sound(os.path.join(self.sound_effect_directory, file_name))
        self.music = {}
        for file_name in os.listdir(self.music_directory):
            self.music[file_name.replace('.wav', '')] = pygame.mixer.Sound(os.path.join(self.music_directory, file_name))

    def set_volume(self, volume):
        self.volume = volume
        for key in self.sounds:
            self.sounds[key].set_volume(volume / 100)
        for key in self.music:
            self.music[key].set_volume(volume / 100)

class snake_game():
    def __init__(self, sound):
        #self.counter = None
        self.tick_speed = 4

        self.size = [20, 10]

        self.snake_color = 0x800080
        self.apple_color = 0xff0000
        self.background_color = 0x00aa44
        self.grass_color = 0x009933
        self.grass = []
        self.grass_count = 45
        self.grass_change_draw_pile = 150
        self.grass_change_periodicity = 150

        self.death_wait_time = 2

        self.sound = sound

    def restart(self, surface_size, snake_head, name, tick_speed):
        pygame.mouse.set_visible(0)
        self.counter = tick_speed / self.tick_speed
        self.quit_squish = 0
        self.alive = 1
        self.update_window_size = 0
        self.reset_joysticks = 0
        self.score = 0
        self.name = name

        if (self.size[0] != -2) and (self.size[1] != -2):
            self.mult = 0.95 * min([surface_size[0] / (self.size[0] + 2), surface_size[1] / (self.size[1] + 2)])
        else:
            self.mult = 60
        self.snake_surface = pygame.Surface([self.size[0], self.size[1]])
        self.yard_surface = pygame.Surface([self.size[0] + 2, self.size[1] + 2])
        self.death_surface = pygame.Surface([(self.size[0] + 2) * self.mult, (self.size[1] + 2) * self.mult])
        self.snake = [[5, 4]]
        valid_spots = []
        for i in range(0, self.size[0]):
            for ii in range(0, self.size[1]):
                valid_spots.append([i, ii])
        for pos in self.snake:
            if valid_spots.count(pos):
                valid_spots.remove(pos)
        self.apple = valid_spots[random.randint(0, len(valid_spots) - 1)]
        self.index = 0
        self.dir = [1, 0]
        self.new_dir = [0, 0]
        self.snake_head = snake_head

        self.grass_change_counter = 0
        self.generate_grass()

        self.death_particle = None
        self.death_wait_cnt = 0
        self.death_particle_p = [0, 0]

        if random.randint(0, 2) == 0:
            song = random.randint(0, 2)
            if song == 0:
                self.sound.music['noisy'].play()
            elif song == 1:
                self.sound.music['pianoing'].play()
            elif song == 2:
                self.sound.music['snoisy'].play()

    def get_inputs(self, players, controllers, joysticks, joystick_threshold, surface_size, su_rects):
        self.counter += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_squish = 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.alive = 0
                elif (event.key == pygame.K_LEFT) or (event.key == pygame.K_a):
                    self.new_dir[0] += -1
                elif (event.key == pygame.K_RIGHT) or (event.key == pygame.K_d):
                    self.new_dir[0] += 1
                elif (event.key == pygame.K_UP) or (event.key == pygame.K_w):
                    self.new_dir[1] += -1
                elif (event.key == pygame.K_DOWN) or (event.key == pygame.K_s):
                    self.new_dir[1] += 1
            elif (event.type == pygame.JOYDEVICEADDED) or (event.type == pygame.JOYDEVICEREMOVED):
                self.reset_joysticks = 1
            elif ((event.type == pygame.JOYBUTTONDOWN) and (event.button == pygame.CONTROLLER_BUTTON_BACK)):
                self.alive = 0
            elif (event.type == pygame.WINDOWRESIZED) or (event.type == pygame.WINDOWMOVED) or (event.type == pygame.WINDOWEXPOSED):
                self.update_window_size = 1

        for kontroller in controllers:
            kontroller.check_snake_inputs(self.new_dir)
        
        key = pygame.key.get_pressed()
        for plajer in players:
            for control_key in plajer.controls:
                control = plajer.controls[control_key][:]
                if control[0] == -1:
                    plajer.controls[control_key][-1] = key[control[1]]
                if len(controllers) > 0:
                    if control[0] >= len(controllers):
                        control[0] %= len(controllers)
                    if control[0] != -1:
                        if control[1] == 'button':
                            if joysticks[control[0]].get_numbuttons() > control[2]:
                                plajer.controls[control_key][-1] = joysticks[control[0]].get_button(control[2])
                        elif control[1] == 'axis':
                            if joysticks[control[0]].get_numaxes() > control[2]:
                                plajer.controls[control_key][-1] = (control[3] * joysticks[control[0]].get_axis(control[2]) >= joystick_threshold)
                        elif control[1] == 'hat':
                            if joysticks[control[0]].get_numhats() > control[2]:
                                plajer.controls[control_key][-1] = (joysticks[control[0]].get_hat(control[2]) == control[3])
            if plajer.controls['left'][-1]:
                self.new_dir[0] += -1
            if plajer.controls['right'][-1]:
                self.new_dir[0] += 1
            if plajer.controls['up'][-1]:
                self.new_dir[1] += -1
            if plajer.controls['down'][-1]:
                self.new_dir[1] += 1

        if self.grass_change_counter >= self.grass_change_periodicity:
            if random.randint(0, self.grass_change_draw_pile) == 0:
                self.change_grass(surface_size, su_rects)
                self.grass_change_counter = 0
        else:
            self.grass_change_counter += 1

    def update_snake(self, surface_size, su_rects):
        self.counter = 0
        if self.dir[0]:
            self.new_dir[0] = 0
        if self.dir[1]:
            self.new_dir[1] = 0
        if self.new_dir != [0, 0]:
            self.dir = keep_within(self.new_dir, -1, 1)
        nindex = (self.index + 1) % len(self.snake)
        new_pos = [self.snake[self.index][0] + self.dir[0], self.snake[self.index][1] + self.dir[1]]
        if (new_pos[0] < 0) or (new_pos[0] >= self.size[0]) or (new_pos[1] < 0) or (new_pos[1] >= self.size[1]):
            self.alive = 0
        elif self.snake.count(new_pos) and (self.snake[(self.index + 1) % len(self.snake)] != new_pos):
            self.alive = 0
        else:
            self.index = nindex
            if new_pos == self.apple:
                self.sound.sounds['eat'].play()
                self.snake.insert(nindex, new_pos)
                self.score += 1
                valid_spots = []
                for i in range(0, self.size[0]):
                    for ii in range(0, self.size[1]):
                        valid_spots.append([i, ii])
                for pos in self.snake:
                    if valid_spots.count(pos):
                        valid_spots.remove(pos)
                self.apple = valid_spots[random.randint(0, len(valid_spots) - 1)]
                self.append_su_rects(surface_size, su_rects, self.apple)
            else:
                self.append_su_rects(surface_size, su_rects, self.snake[nindex])
                self.snake[nindex] = new_pos
            self.append_su_rects(surface_size, su_rects, self.snake[(nindex - 1) % len(self.snake)])
            self.append_su_rects(surface_size, su_rects, new_pos)
            self.new_dir = [0, 0]

    def generate_grass(self):
        self.grass = []
        for i in range(0, self.grass_count):
            self.grass.append([random.randint(0, self.size[0] - 1), random.randint(0, self.size[1] - 1)])

    def change_grass(self, surface_size, su_rects):
        i = random.randint(0, len(self.grass) - 1)
        self.append_su_rects(surface_size, su_rects, self.grass[i])
        self.grass[i] = [random.randint(0, self.size[0] - 1), random.randint(0, self.size[1] - 1)]
        self.append_su_rects(surface_size, su_rects, self.grass[i])

    def display_snake(self, display):
        display.fill(self.background_color)
        self.snake_surface.fill(self.background_color)
        for pos in self.grass:
            self.snake_surface.set_at(pos, self.grass_color)
        self.snake_surface.set_at(self.apple, self.apple_color)
        for i in range(0, len(self.snake)):
            self.snake_surface.set_at(self.snake[i], self.snake_color)
        self.snake_surface.set_at(self.snake[self.index], self.snake_head)
        self.yard_surface.fill(0x7b4d33)
        self.yard_surface.blit(self.snake_surface, [1, 1])
        display.blit(pygame.transform.scale(self.yard_surface, [(self.size[0] + 2) * self.mult, (self.size[1] + 2) * self.mult]), [0.5 * display.get_size()[0] - 0.5 * self.yard_surface.get_size()[0] * self.mult, 0.5 * display.get_size()[1] - 0.5 * self.yard_surface.get_size()[1] * self.mult])

    def update_death(self):
        if self.death_particle == None:
            if self.death_wait_cnt < self.death_wait_time:
                self.death_wait_cnt += 1
            else:
                if len(self.snake) == 1:
                    self.sound.sounds['zsz'].play()
                else:
                    self.sound.sounds['snake_die'].play()
                self.death_wait_cnt = 0
                new_index = self.index
                if self.index + 1 == len(self.snake):
                    new_index = (self.index - 1) % len(self.snake)
                pos = self.snake.pop((self.index + 1) % len(self.snake))
                p = [(pos[0] + 1.5) * self.mult, (pos[1] + 1.5) * self.mult]
                s = [self.mult, self.mult]
                self.death_particle = death_animation(p, s)
                self.death_particle_p = pos[:]
                self.index = new_index

    def display_death(self, display, su_rects):
        surface_size = display.get_size()
        display.fill(self.background_color)
        self.snake_surface.fill(self.background_color)
        for pos in self.grass:
            self.snake_surface.set_at(pos, self.grass_color)
        self.snake_surface.set_at(self.apple, self.apple_color)
        if len(self.snake):
            for pos in self.snake:
                self.snake_surface.set_at(pos, self.snake_color)
            self.snake_surface.set_at(self.snake[self.index], self.snake_head)
        self.yard_surface.fill(0x7b4d33)
        self.yard_surface.blit(self.snake_surface, [1, 1])
        self.death_surface.blit(pygame.transform.scale(self.yard_surface, self.death_surface.get_size()), [0, 0])
        if self.death_particle != None:
            for rect in self.death_particle.get_rects():
                pygame.draw.rect(self.death_surface, self.death_particle.color, rect)
            if self.death_particle.life <= 0:
                self.death_particle = None
        self.append_su_rects(surface_size, su_rects, self.death_particle_p)
        display.blit(self.death_surface, [0.5 * display.get_size()[0] - 0.5 * self.death_surface.get_size()[0], 0.5 * display.get_size()[1] - 0.5 * self.death_surface.get_size()[1]])

    def append_su_rects(self, surface_size, su_rects, ip):
        c = [0.5 * surface_size[0] - 0.5 * self.yard_surface.get_size()[0] * self.mult, 0.5 * surface_size[1] - 0.5 * self.yard_surface.get_size()[1] * self.mult]
        p = [c[0] + self.mult * (0.9 + ip[0]), c[1] + self.mult * (1 + ip[1])]
        s = [1.2 * self.mult, 1.2 * self.mult]
        su_rects.append([p, s])

    def ask_for_quit(self):
        return (self.death_particle == None) and (len(self.snake) <= 0) and (self.death_wait_cnt >= self.death_wait_time)

class scythe_game():
    def __init__(self, cwd, sound):
        self.cwd = cwd
        self.size_grid = [20, 10]
        self.size_image = [10, 10]
        self.size = [self.size_grid[0] * self.size_image[0], self.size_grid[1] * self.size_image[1]]
        self.size_with_fence = [self.size[0] + 2 * self.size_image[0], self.size[1] + 2 * self.size_image[1]]
        self.surface = pygame.Surface(self.size_with_fence)
        self.size_wide = [self.size_with_fence[0] + 2 * self.size_image[0], self.size_with_fence[1] + 2 * self.size_image[1]]
        self.surface_2 = pygame.Surface(self.size_wide)
        self.color_key = 0x010101
        self.grass_color = 0x009933
        self.load_images()

        self.flower_count = 25
        self.flower_change_periodicity = 150
        self.flower_change_draw_pile = 150

        self.sheep_count = 20
        self.baa_chance = 0.008
        
        self.wolf_spawn_periodicity = 50
        self.wolf_spawn_draw_pile = 200

        self.attack_time = 25
        self.kill_radius_wolf = 10
        self.kill_radius_sheep = 8
        
        self.xmin = self.size_image[0]
        self.xmax = self.size_with_fence[0] - self.size_image[0]
        self.ymin = self.size_image[1]
        self.ymax = self.size_with_fence[1] - self.size_image[1]
        self.bounds = [[self.xmin, self.xmax], [self.ymin, self.ymax]]

        self.score_multiplier = 0.005
        self.score = 0

        self.sound = sound

    def load_images(self):
        self.sprite_directory = os.path.join(self.cwd, 'sprites')
        self.img_flower_1 = self.load_image('flower_1.png')
        self.img_flower_2 = self.load_image('flower_2.png')
        self.img_sheep_right = self.load_image('sheep.png')
        self.img_sheep_left = pygame.transform.flip(self.img_sheep_right, 1, 0)
        self.img_wolf_right = self.load_image('wolf.png')
        self.img_wolf_left = pygame.transform.flip(self.img_wolf_right, 1, 0)
        self.img_player_right = self.load_image('player.png')
        self.img_player = self.img_player_right
        self.img_player_left = pygame.transform.flip(self.img_player, 1, 0)
        self.img_scythe_right = self.load_image('scythe.png')
        self.img_scythe = self.img_scythe_right
        self.img_scythe_left = pygame.transform.flip(self.img_scythe, 1, 0)
        self.img_scythe_attack_right = pygame.transform.rotate(self.img_scythe, 90)
        self.img_scythe_attack_left = pygame.transform.flip(self.img_scythe_attack_right, 1, 0)
        self.img_scythe_attack = self.img_scythe_attack_left
        self.img_fence_corner_1 = self.load_image('fence_corner_1.png')
        self.img_fence_corner_2 = self.load_image('fence_corner_2.png')
        self.img_fence_corner_3 = self.load_image('fence_corner_3.png')
        self.img_fence_corner_4 = self.load_image('fence_corner_4.png')
        self.img_fence_horizontal = self.load_image('fence_horizontal.png')
        self.img_fence_vertical = self.load_image('fence_vertical.png')
        self.img_fence_vertical_post = self.load_image('fence_vertical_post.png')
        self.img_fence_vertical_beam = self.load_image('fence_vertical_beam.png')

        self.surface_fence_upper = pygame.Surface(self.size_with_fence)
        self.surface_fence_upper.fill(self.grass_color)
        self.surface_fence_upper.blit(self.img_fence_corner_1, [0, 0])
        self.surface_fence_upper.blit(self.img_fence_corner_2, [self.size[0] + self.size_image[0], 0])
        self.surface_fence_upper.blit(self.img_fence_corner_3, [0, self.size[1] + self.size_image[1]])
        self.surface_fence_upper.blit(self.img_fence_corner_4, [self.size[0] + self.size_image[0], self.size[1] + self.size_image[1]])
        for x in range(0, self.size_grid[0]):
            self.surface_fence_upper.blit(self.img_fence_horizontal, [self.size_image[0] * (x + 1), 0])
        for x in [0, self.size[0] + self.size_image[0]]:
            for y in range(0, self.size_grid[1]):
                self.surface_fence_upper.blit(self.img_fence_vertical, [x, self.size_image[1] * (y + 1)])
        
        self.surface_fence_beam_sides = pygame.Surface([self.size_with_fence[0], self.size_with_fence[1] - 16])
        self.surface_fence_beam_sides.set_colorkey(self.color_key)
        self.surface_fence_beam_sides.fill(self.color_key)
        for x in [0, self.size[0] + self.size_image[0]]:
            for y in range(0, self.size_grid[1] + 2):
                self.surface_fence_beam_sides.blit(self.img_fence_vertical_beam, [x, self.size_image[1] * y - 8])
        
        self.surface_fence_post_sides = pygame.Surface([self.size_with_fence[0], self.size_image[1]])
        self.surface_fence_post_sides.set_colorkey(self.color_key)
        self.surface_fence_post_sides.fill(self.color_key)
        for x in [0, self.size[0] + self.size_image[0]]:
            self.surface_fence_post_sides.blit(self.img_fence_vertical_post, [x, 0])
        
        self.surface_fence_lower = pygame.Surface([self.size_with_fence[0], 7])
        self.surface_fence_lower.set_colorkey(self.color_key)
        self.surface_fence_lower.fill(self.color_key)
        self.surface_fence_lower.blit(self.img_fence_corner_3, [0, -2])
        self.surface_fence_lower.blit(self.img_fence_corner_4, [self.size[0] + self.size_image[0], -2])
        for x in range(0, self.size_grid[0]):
            self.surface_fence_lower.blit(self.img_fence_horizontal, [10 * (x + 1), -2])

    def load_image(self, file_name):
        image = pygame.image.load(os.path.join(self.sprite_directory, file_name)).convert()
        image.set_colorkey(self.color_key)
        return image

    def restart(self, surface_size):
        pygame.mouse.set_visible(0)
        self.quit_squish = 0
        self.running = 1
        self.game_over = 0
        self.update_window_size = 0
        self.reset_joysticks = 0
        self.score = 0
        if (self.size[0] != -2) and (self.size[1] != -2):
            self.mult = 0.85 * min([surface_size[0] / (self.size[0] + 2), surface_size[1] / (self.size[1] + 2)])
        else:
            self.mult = 8
        self.flower_change_counter = 0
        self.generate_flowers()

        self.img_player = self.img_player_right
        self.img_scythe = self.img_scythe_right
        self.img_scythe_attack = self.img_scythe_attack_left

        self.player_pos = [0.5 * self.size_with_fence[0], 0.25 * self.size_with_fence[1]]
        self.player_pos_a = self.player_pos[:]
        self.player_lpos_a = self.player_pos[:]
        self.player_dir = [0, 0]
        self.player_vel_desired = [0, 0]
        self.player_vel = [0, 0]
        self.player_vel_delta = [0.1, 0.1]
        self.player_vel_terminal = [1, 1]

        self.scythe_pos = [0, 0]
        self.lscythe_pos = [0, 0]
        self.scythe_shift = [round(-0.8 * self.size_image[0]), round(0.1 * self.size_image[1])]
        self.attack_pos = [0, 0]
        self.lattack_pos = [0, 0]
        self.attack_shift = [round(0.5 * self.size_image[0]), round(0.4 * self.size_image[1])]
        self.attack = 0

        self.sheep = []
        for i in range(0, self.sheep_count):
            self.sheep.append(scythe_sheep(self.img_sheep_right, self.img_sheep_left, self.xmin, self.xmax, self.ymin, self.ymax))
        
        self.wolves = []
        self.wolf_spawn_counter = 0
        
        self.death_particles = []

        for key in self.sound.music:
            self.sound.music[key].stop()
        
        if random.randint(0, 6) == 0:
            if random.randint(0, 1):
                self.sound.music['pianoing'].play()
            else:
                self.sound.music['plain_piano'].play()

    def get_inputs(self, controllers):
        for event in pygame.event.get():
            self.player_dir = [0, 0]
            if event.type == pygame.QUIT:
                self.quit_squish = 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_over = 1
                    self.generate_death_particle()
            elif (event.type == pygame.JOYDEVICEADDED) or (event.type == pygame.JOYDEVICEREMOVED):
                self.reset_joysticks = 1
            elif ((event.type == pygame.JOYBUTTONDOWN) and (event.button == pygame.CONTROLLER_BUTTON_BACK)):
                self.game_over = 1
                self.generate_death_particle()
            elif (event.type == pygame.WINDOWRESIZED) or (event.type == pygame.WINDOWMOVED) or (event.type == pygame.WINDOWEXPOSED):
                self.update_window_size = 1

        for kontroller in controllers:
            kontroller.check_scythe_inputs(self.player_dir)
            if kontroller.controls['jump'][0] or kontroller.controls['shield'][0] or kontroller.controls['select'][0]:
                if self.attack <= 0:
                    self.attack = self.attack_time
        
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            self.player_dir[0] += -1
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            self.player_dir[0] += 1
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
            self.player_dir[1] += -1
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            self.player_dir[1] += 1
        
        if pressed_keys[pygame.K_SPACE]:
            if self.attack <= 0:
                self.attack = self.attack_time

    def update_scythe(self, surface_size, su_rects):
        for sheep in self.sheep:
            sheep.change_dir()
            sheep.bob()
            sheep.move()
        
        if random.random() <= self.baa_chance:
            if random.randint(0, 1):
                self.sound.sounds['baa_1'].play()
            else:
                self.sound.sounds['baa_2'].play()
        
        self.player_lpos_a = self.player_pos_a[:]
        self.player_dir = keep_within(self.player_dir, -1, 1)
        self.player_vel_desired = [self.player_vel_terminal[0] * self.player_dir[0], self.player_vel_terminal[1] * self.player_dir[1]]
        for i in range(0, 2):
            if abs(self.player_vel[i] - self.player_vel_desired[i]) <= self.player_vel_delta[i]:
                self.player_vel[i] = self.player_vel_desired[i]
            elif self.player_vel[i] < self.player_vel_desired[i]:
                self.player_vel[i] += self.player_vel_delta[i]
            elif self.player_vel[i] > self.player_vel_desired[i]:
                self.player_vel[i] += -self.player_vel_delta[i]
            self.player_pos[i] += self.player_vel[i]
            self.player_pos[i] = keep_within(self.player_pos[i], self.bounds[i][0], self.bounds[i][1])
            self.player_pos_a[i] = self.player_pos[i] - 0.5 * self.size_image[i]

            if self.player_dir[0] > 0:
                self.img_player = self.img_player_right
                self.img_scythe = self.img_scythe_right
                self.img_scythe_attack = self.img_scythe_attack_left
                self.scythe_shift[0] = round(-0.8 * self.size_image[0])
                self.attack_shift[0] = round(0.5 * self.size_image[0])
            elif self.player_dir[0] < 0:
                self.img_player = self.img_player_left
                self.img_scythe = self.img_scythe_left
                self.img_scythe_attack = self.img_scythe_attack_right
                self.scythe_shift[0] = round(0.8 * self.size_image[0])
                self.attack_shift[0] = round(-0.5 * self.size_image[0])
        
        self.lattack_pos = self.attack_pos[:]
        self.lscythe_pos = self.scythe_pos[:]
        self.scythe_pos = [self.player_pos_a[0] + self.scythe_shift[0] + self.size_image[0], self.player_pos_a[1] + self.scythe_shift[1]]
        self.attack_pos = [self.player_pos_a[0] + self.attack_shift[0] + self.size_image[0], self.player_pos_a[1] + self.attack_shift[1]]
        if self.attack == self.attack_time:
            self.sound.sounds['un_sheath'].play()
        if self.attack > 0:
            self.attack += -1
        
        if self.flower_change_counter >= self.flower_change_periodicity:
            if random.randint(0, self.flower_change_draw_pile) == 0:
                self.change_flowers(surface_size, su_rects)
                self.flower_change_counter = 0
        else:
            self.flower_change_counter += 1

        for wolf in self.wolves:
            wolf.update(self.sheep, self.player_pos)
        
        wolf_kill_list = []
        if self.attack > 0.3 * self.attack_time:
            for i in range(0, len(self.wolves)):
                wolf = self.wolves[i]
                if distance(wolf.pos, [self.attack_pos[0] - 0.5 * self.size_image[0], self.attack_pos[1] + 0.5 * self.size_image[1]]) <= self.kill_radius_wolf:
                    wolf_kill_list.append(i)
        wolf_kill_list.sort(reverse = 1)
        for i in wolf_kill_list:
            wolf = self.wolves.pop(i)
            self.sound.sounds['wimper'].play()
            self.death_particles.append(death_animation(wolf.pos, self.size_image, 10, [0xff0000, 0x000000, 0x000000, 0xffffff]))
            self.append_su_rects(surface_size, su_rects, wolf.lpos_a)
        
        sheep_kill_list = []
        for wolf in self.wolves:
            for i in range(0, len(self.sheep)):
                if sheep_kill_list.count(i) == 0:
                    if distance(self.sheep[i].pos, wolf.pos) <= self.kill_radius_sheep:
                        sheep_kill_list.append(i)
        sheep_kill_list.sort(reverse = 1)
        for i in sheep_kill_list:
            sheep = self.sheep.pop(i)
            self.sound.sounds['wolf_eat'].play()
            self.death_particles.append(death_animation(sheep.pos, self.size_image, 10, [0x000000, 0x000000, 0xff0000, 0xffffff]))
            self.append_su_rects(surface_size, su_rects, sheep.lpos_a)
        
        self.score += self.score_multiplier * len(self.sheep)

        if len(self.sheep) <= 0:
            self.generate_death_particle()

        spawn_increaser = len(self.sheep) / self.sheep_count
        if self.wolf_spawn_counter >= self.wolf_spawn_periodicity * spawn_increaser:
            if random.randint(0, round(self.wolf_spawn_draw_pile * spawn_increaser)) == 0:
                self.wolves.append(scythe_wolf(self.sheep, self.img_wolf_right, self.img_wolf_left, self.xmin, self.xmax, self.ymin, self.ymax))
                self.sound.sounds['howl'].play()
                self.wolf_spawn_counter = 0
        else:
            self.wolf_spawn_counter += 1
        
        if not len(self.sheep):
            self.game_over = 1
            self.generate_death_particle()

    def generate_flowers(self):
        self.surface_flowers = self.surface_fence_upper.copy()
        self.flowers = []
        for i in range(0, self.flower_count):
            flower = [round(random.randint(0, self.size[1] - 1) + 0.5 * self.size_image[0]), round(random.randint(0, self.size[0] - 1) + 0.5 * self.size_image[1]), random.randint(1, 2)]
            self.flowers.append(flower)
        self.flowers.sort()
        for flower in self.flowers:
            if flower[2] == 1:
                image = self.img_flower_1
            elif flower[2] == 2:
                image = self.img_flower_2
            self.surface_flowers.blit(image, [flower[1], flower[0]])

    def change_flowers(self, surface_size, su_rects):
        self.surface_flowers = self.surface_fence_upper.copy()
        i = random.randint(0, len(self.flowers) - 1)
        flower = [round(random.randint(0, self.size[1] - 1) + 0.5 * self.size_image[0]), round(random.randint(0, self.size[0] - 1) + 0.5 * self.size_image[1]), random.randint(1, 2)]
        self.append_su_rects(surface_size, su_rects, [self.flowers[i][1], self.flowers[i][0]])
        self.flowers[i] = flower
        self.append_su_rects(surface_size, su_rects, [self.flowers[i][1], self.flowers[i][0]])
        self.flowers.sort()
        for flower in self.flowers:
            if flower[2] == 1:
                image = self.img_flower_1
            elif flower[2] == 2:
                image = self.img_flower_2
            self.surface_flowers.blit(image, [flower[1], flower[0]])

    def generate_death_particle(self):
        self.sound.sounds['zsz'].play()
        p = self.player_pos
        s = [round(2.5 * self.size_image[0]), round(2.5 * self.size_image[1])]
        self.death_particles.append(death_animation(p, s, 75, [0xaa0000, 0x000000, 0x000000]))

    def display_scythe(self, display, su_rects, game_instance):
        surface_size = display.get_size()
        self.surface.blit(self.surface_flowers, [0, 0])
        for i in range(0, self.size_grid[1] + 1):
            y = i * self.size_image[1]
            if i > 0:
                self.surface.blit(self.surface_fence_post_sides, [0, y])
            if (y <= self.player_pos[1] - 4) and (self.player_pos[1] - 4 < y + self.size_image[1]):
                if not self.game_over:
                    self.surface.blit(self.img_player, self.player_pos_a)
        self.append_su_rects(surface_size, su_rects, self.player_lpos_a)
        self.append_su_rects(surface_size, su_rects, self.player_pos_a)
        self.surface.blit(self.surface_fence_beam_sides, [0, 8])
        for sheep in self.sheep:
            self.surface.blit(sheep.image, sheep.pos_a)
            self.append_su_rects(surface_size, su_rects, sheep.lpos_a)
            self.append_su_rects(surface_size, su_rects, sheep.pos_a)
        for wolf in self.wolves:
            self.surface.blit(wolf.image, wolf.pos_a)
            self.append_su_rects(surface_size, su_rects, wolf.lpos_a)
            self.append_su_rects(surface_size, su_rects, wolf.pos_a)
        
        kill_particles = []
        for i in range(0, len(self.death_particles)):
            particle = self.death_particles[i]
            if particle.life <= 0:
                kill_particles.append(i)
        kill_particles.sort(reverse = 1)
        for i in kill_particles:
            particle = self.death_particles.pop(i)
            for rect in particle.rects:
                self.append_su_rects(surface_size, su_rects, rect[0])
        
        for i in range(0, len(self.death_particles)):
            particle = self.death_particles[i]
            for rect in particle.get_rects():
                pygame.draw.rect(self.surface, particle.color, rect)
                self.append_su_rects(surface_size, su_rects, rect[0])
            for rect in particle.lrects:
                self.append_su_rects(surface_size, su_rects, rect[0])

        self.surface_2.fill(self.grass_color)
        self.surface_2.blit(self.surface, [self.size_image[0], 0])
        if not self.game_over:
            if self.attack > 0.3 * self.attack_time:
                self.surface_2.blit(self.img_scythe_attack, self.attack_pos)
            else:
                self.surface_2.blit(self.img_scythe, self.scythe_pos)
        self.append_su_rects(surface_size, su_rects, self.lattack_pos, 1)
        self.append_su_rects(surface_size, su_rects, self.attack_pos, 1)
        self.append_su_rects(surface_size, su_rects, self.lscythe_pos, 1)
        self.append_su_rects(surface_size, su_rects, self.scythe_pos, 1)
        self.surface_2.blit(self.surface_fence_lower, [self.size_image[0], self.size[1] + self.size_image[1] + 2])

        display.fill(self.grass_color)
        display.blit(pygame.transform.scale(self.surface_2, [self.size_wide[0] * self.mult, self.size_wide[1] * self.mult]), [0.5 * display.get_size()[0] - 0.5 * self.size_wide[0] * self.mult, 0.5 * display.get_size()[1] - 0.5 * self.size_with_fence[1] * self.mult])
        
        display_size = display.get_size()
        [img, s] = game_instance.text2img(str(round(self.score)), 0, 'couriernew', 48, 1)
        pygame.draw.rect(display, 0x5e3926, [[display_size[0] - 8.45 * s[1], 0.57 * s[1]], [3.62 * s[1], 1.3 * s[1]]])
        pygame.draw.rect(display, 0xab6a47, [[display_size[0] - 8.27 * s[1], 0.75 * s[1]], [3.27 * s[1], 0.945 * s[1]]])
        p = [display_size[0] - 5.17 * s[1] - s[0], 0.75 * s[1]]
        display.blit(img, p)
        su_rects.append([p, s])

    def append_su_rects(self, surface_size, su_rects, ip, alt = 0):
        if not alt:
            c = [0.5 * surface_size[0] - 0.5 * self.size_with_fence[0] * self.mult, 0.5 * surface_size[1] - 0.5 * self.size_with_fence[1] * self.mult]
        else:
            c = [0.5 * surface_size[0] - 0.5 * self.size_wide[0] * self.mult, 0.5 * surface_size[1] - 0.5 * self.size_with_fence[1] * self.mult]
        p = [c[0] + (ip[0] - 3) * self.mult, c[1] + (ip[1] - 3) * self.mult]
        s = [self.mult * (self.size_image[0] + 6), self.mult * (self.size_image[1] + 6)]
        su_rects.append([p, s])

class scythe_sheep():
    def __init__(self, image_right, image_left, xmin, xmax, ymin, ymax):
        self.pos = [xmin + (random.random()) * (xmax - xmin), ymin + (random.random()) * (ymax - ymin)]
        self.pos_a = self.pos[:]
        self.lpos_a = self.pos[:]
        self.size = image_right.get_size()
        self.vel = [0, 0]
        self.speed = 0.1
        self.dir = [0, 0]
        self.dir_options = [[[-3, -3], 1], [[-1, -3], 2], [[0, -3], 2], [[1, -3], 2], [[3, -3], 1],
                            [[-3, -1], 2], [[-1, -1], 4], [[0, -1], 4], [[1, -1], 4], [[3, -1], 2],
                            [[-3,  0], 2], [[-1,  0], 4], [[0, 0], 20], [[1,  0], 4], [[3,  0], 2],
                            [[-3,  1], 2], [[-1,  1], 4], [[0,  1], 4], [[1,  1], 4], [[3,  1], 2],
                            [[-3,  3], 1], [[-1,  3], 2], [[0,  3], 2], [[1,  3], 2], [[3,  3], 1]]
        self.dir_weights = []
        for i in range(0, len(self.dir_options)):
            self.dir_weights += [i] * self.dir_options[i][1]
        self.dir_change_periodicity = 50
        self.dir_change_draw_pile = 50
        self.dir_change_count = 0
        self.image_left = image_left.copy()
        self.image_right = image_right.copy()
        if random.randint(0, 1):
            self.image = self.image_right
        else:
            self.image = self.image_left
        self.dy = 0
        self.dy_x = 0
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
    
    def change_dir(self, override = 0):
        if self.dir_change_count >= self.dir_change_periodicity:
            if random.randint(0, self.dir_change_draw_pile) == 0:
                i = self.dir_weights[random.randint(0, len(self.dir_weights) - 1)]
                self.dir = self.dir_options[i][0]
                if self.dir[0] > 0:
                    self.image = self.image_right
                elif self.dir[0] < 0:
                    self.image = self.image_left
                self.dir_change_count = 0
        else:
            self.dir_change_count += 1

    def move(self):
        self.lpos_a = self.pos_a
        self.pos[0] += self.dir[0] * self.speed
        if self.pos[0] < self.xmin:
            self.pos[0] = self.xmin
        elif self.pos[0] > self.xmax:
            self.pos[0] = self.xmax
        self.pos[1] += self.dir[1] * self.speed
        if self.pos[1] < self.ymin:
            self.pos[1] = self.ymin
        elif self.pos[1] > self.ymax:
            self.pos[1] = self.ymax
        self.pos_a = [self.pos[0] - 0.5 * self.size[0], self.pos[1] + self.dy - 0.5 * self.size[1]]
        
    def bob(self):
        if (self.dir != [0, 0]) or (self.dy_x != 0):
            if self.dy_x > 50:
                self.dy_x = 0
            if self.dy_x > 30:
                self.dy = 0
            else:
                self.dy = 0.008 * (self.dy_x * (self.dy_x - 30))
            self.dy_x += 1
            if magnitude(self.dir) >= 3:
                self.dy_x += 1

class scythe_wolf():
    def __init__(self, sheep, image_right, image_left, xmin, xmax, ymin, ymax):
        self.image_right = image_right
        self.image = self.image_right
        self.image_left = image_left
        self.image_size = image_right.get_size()

        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

        self.find_spawn_point(sheep, 10)
        self.lpos = self.pos[:]
        self.pos_a = self.pos[:]
        self.lpos_a = self.pos[:]

        self.desired_pos = []
        self.vel = [0, 0]
        self.lvel = [0, 0]
        self.vel_delta = 0.15
        self.vel_terminal = 0.8
        self.vel_std = 0.01
        self.flee_radius = 40

    def find_spawn_point(self, sheep, cnt):
        if len(sheep):
            possible_poses = cnt * [[0, 0]]
            distances = cnt * [0]
            for i in range(0, cnt):
                possible_poses[i] = [random.randint(self.xmin, self.xmax), random.randint(self.ymin, self.ymax)]
                sheep_pos = self.nearest_sheep_pos(sheep, possible_poses[i])
                distances[i] = distance(sheep_pos, possible_poses[i])
            self.pos = possible_poses[distances.index(max(distances))]
        else:
            self.pos = [random.randint(self.xmin, self.xmax), random.randint(self.ymin, self.ymax)]

    def update(self, sheep, player_pos):
        self.lpos_a = self.pos_a
        self.lvel = [self.pos[0] - self.lpos[0], self.pos[1] - self.lpos[1]]
        self.lpos = self.pos[:]
        if (distance(player_pos, self.pos) <= self.flee_radius) and (-1 / (len(sheep) + 0.001) + 1 > random.random()):
            self.desired_pos = [2 * self.pos[0] - player_pos[0], 2 * self.pos[1] - player_pos[1]]
        else:
            self.desired_pos = self.nearest_sheep_pos(sheep)

        magn = distance(self.desired_pos, self.pos)
        if magn != 0:
            for i in range(0, 2):
                self.vel[i] += self.vel_delta * (self.desired_pos[i] - self.pos[i]) / magn
        
        magn = magnitude(self.lvel)
        if 1 / (magn + 0.01) > random.randint(0, 100):
            for i in range(0, 2):
                self.vel[i] += self.vel_terminal * 2 * (random.random() - 0.5)
        
        magn = magnitude(self.vel)
        if (magn > self.vel_terminal) and (magn != 0):
            for i in range(0, 2):
                self.vel[i] = self.vel[i] * self.vel_terminal / magn

        if self.pos[0] + self.vel[0] > self.xmax:
            self.pos[0] = self.xmax
        elif self.pos[0] + self.vel[0] < self.xmin:
            self.pos[0] = self.xmin
        else:
            self.pos[0] += self.vel[0]
        if self.pos[1] + self.vel[1] > self.ymax:
            self.pos[1] = self.ymax
        elif self.pos[1] + self.vel[1] < self.ymin:
            self.pos[1] = self.ymin
        else:
            self.pos[1] += self.vel[1]
        
        if self.vel[0] > 0:
            self.image = self.image_right
        elif self.vel[0] < 0:
            self.image = self.image_left

        self.pos_a = [self.pos[0] - 0.5 * self.image_size[0], self.pos[1] - 0.5 * self.image_size[1]]

    def nearest_sheep_pos(self, sheep, pos = None):
        if len(sheep):
            if pos == None:
                pos = self.pos
            distances = len(sheep) * [0]
            for ii in range(0, len(sheep)):
                distances[ii] = distance(pos, sheep[ii].pos)
            return sheep[distances.index(min(distances))].pos
        return self.pos

class tron_game():
    def __init__(self, sound):
        self.size = [1920, 1080]
        self.size_player = [60, 60]
        self.size_trail = [0.4 * self.size_player[0], 0.5 * self.size_player[0]]
        self.size_arena = [self.size[0] - 2 * self.size_player[0], self.size[1] - 2 * self.size_player[1]]

        self.color_background = 0x585858
        self.color_walls = 0x000000
        self.colorkey = 0x010101

        self.delta_din = 5
        self.speed = 6
        self.length = 150
        self.trail_rate = 2
        self.trail_accent = 0x4136d7
        self.trail_animation_periodicity = 4

        self.load_image()

        self.sound = sound

    def load_image(self):
        self.surface = pygame.Surface(self.size)
        self.load_trail_surface()
        self.surface_dead_trail = pygame.Surface(self.size_trail)
        self.surface_dead_trail.set_colorkey(self.colorkey)
        self.surface_dead_trail.fill(self.color_background)
        self.surface_wall = pygame.Surface(self.size)
        self.surface_wall.set_colorkey(self.colorkey)
        self.surface_wall.fill(self.color_walls)
        self.surface_wall.fill(self.colorkey, [self.size_player, self.size_arena])

    def load_trail_surface(self):
        self.surface_trail = pygame.Surface(self.size)
        self.surface_trail.fill(self.color_background)
    
    def restart(self, players, team_count, team_colors):
        pygame.mouse.set_visible(0)
        self.team_count = team_count
        self.team_colors = team_colors
        wall_length = 2 * self.size_arena[0] + 2 * self.size_arena[1]
        if len(players):
            next_step = wall_length / len(players)
        else:
            next_step = 0
        step_remaining = next_step
        w1 = 1 * self.size_player[0]
        w2 = 1 * self.size_player[1]
        w3 = self.size[0] - self.size_player[0]
        w4 = self.size[1] - self.size_player[1]
        next_pos = [self.size_player[0], 0.5 * self.size[1]]
        next_din = 0
        self.players = []
        for i in range(0, len(players)):
            plajer = players[i]
            self.players.append(tron_player(plajer, next_pos, next_din, self.delta_din, self.speed, self.size_player[0], self.size_trail, self.length, self.trail_rate, self.trail_accent, self.colorkey, self.team_count, self.team_colors))
            if i < len(players) - 1:
                while step_remaining > 0:
                    if next_pos[0] <= w1:
                        if step_remaining < next_pos[1] - w2:
                            next_pos[1] -= step_remaining
                            step_remaining = 0
                        else:
                            step_remaining -= next_pos[1] - w2
                            next_pos[1] = w2
                        next_din = 0
                    if next_pos[1] <= w2:
                        if step_remaining < w3 - next_pos[0]:
                            next_pos[0] += step_remaining
                            step_remaining = 0
                        else:
                            step_remaining -= w3 - next_pos[0]
                            next_pos[0] = w3
                        next_din = 90
                    if next_pos[0] >= w3:
                        if step_remaining < w4 - next_pos[1]:
                            next_pos[1] += step_remaining
                            step_remaining = 0
                        else:
                            step_remaining -= w4 - next_pos[1]
                            next_pos[1] = w4
                        next_din = 180
                    if next_pos[1] >= w4:
                        if step_remaining < next_pos[0] - w1:
                            next_pos[0] -= step_remaining
                            step_remaining = 0
                        else:
                            step_remaining -= next_pos[0] - w1
                            next_pos[0] = w1
                        next_din = 270
                step_remaining = next_step
        self.dont_kill = 8
        self.death_animations = []
        self.dead_trails = []
        self.winner = None
        self.death_wait_time = 10
        self.load_trail_surface()

        if not self.sound.music['noisy'].get_num_channels():
            if random.randint(0, 5) == 0:
                self.sound.music['noisy'].play()

    def run(self):
        for plajer in self.players:
            plajer.move()
        
        kill_players = []
        if not self.dont_kill:
            for i in range(0, len(self.players)):
                plajer = self.players[i]
                for ii in range(0, len(self.players)):
                    plaier = self.players[ii]
                    # Collide with player
                    if i != ii:
                        if distance(plajer.pos, plaier.pos) < 0.8 * self.size_player[0]:
                            kill_players.append(i)
                    
                    # Collide with trail
                    for iii in range(0, len(plaier.trail)):
                        trail = plaier.trail[iii]
                        if trail != None:
                            if (plaier.trail_index - 1 - iii) % len(plaier.trail) > 3:
                                if distance(plajer.pos, trail[0]) < 0.5 * (self.size_trail[1] + self.size_player[0]):
                                    kill_players.append(i)
                                    if i != ii:
                                        plaier.player.kills += 1
                                    break

                # Collide with wall
                if plajer.pos[0] < 1.5 * self.size_player[0]:
                    kill_players.append(i)
                elif plajer.pos[0] > self.size[0] - 1.5 * self.size_player[0]:
                    kill_players.append(i)
                elif plajer.pos[1] < 1.5 * self.size_player[1]:
                    kill_players.append(i)
                elif plajer.pos[1] > self.size[1] - 1.5 * self.size_player[1]:
                    kill_players.append(i)
        
        if self.dont_kill > 0:
            self.dont_kill += -1

        kill_players.sort(reverse = 1)
        kill_players = remove_redundancy(kill_players)
        for i in kill_players:
            # Create new death animations
            plajer = self.players.pop(i)
            p = plajer.pos
            s = [1.5 * plajer.size[0], 1.5 * plajer.size[1]]
            c = [0x000000, 0x000000, 0x000000]
            c[random.randint(0, len(c) - 1)] = plajer.color
            self.death_animations.append(death_animation(p, s, colors = c))

            self.sound.sounds['zsz'].play()

            # Create animations along the trail
            for ii in range(0, len(plajer.trail)):
                trail = plajer.trail[ii]
                if trail:
                    self.dead_trails.append(trail)
                if (ii % self.trail_animation_periodicity) == 0:
                    iii = (plajer.trail_index + ii) % len(plajer.trail)
                    trail = plajer.trail[iii]
                    if trail:
                        p = trail[0]
                        s = [plajer.trail_size[1], plajer.trail_size[1]]
                        c = [0x000000, 0x000000, 0x000000]
                        c[random.randint(0, len(c) - 1)] = plajer.color
                        self.death_animations.append(death_animation(p, s, colors = c))

    def display(self, su_rects):
        # Remove old trails
        while len(self.dead_trails):
            trail = self.dead_trails.pop()
            img = pygame.transform.rotate(self.surface_dead_trail, -trail[1])
            s = img.get_size()
            p = [trail[0][0] - 0.5 * s[0], trail[0][1] - 0.5 * s[1]]
            self.surface_trail.blit(img, p)
            self.append_su_rects(su_rects, [p, s])
        
        # Display player trails
        for plajer in self.players:
            if plajer.trail_cnt == 0:
                trail = plajer.trail[(plajer.trail_index - 2) % len(plajer.trail)]
                img = pygame.transform.rotate(plajer.img_trail, -trail[1])
                s = img.get_size()
                p = [trail[0][0] - 0.5 * s[0], trail[0][1] - 0.5 * s[1]]
                self.surface_trail.blit(img, p)
                self.append_su_rects(su_rects, [p, s])
                if plajer.trail[plajer.trail_index]:
                    self.dead_trails.append(plajer.trail[plajer.trail_index])
        
        self.surface.blit(self.surface_trail, [0, 0])
        self.surface.blit(self.surface_wall, [0, 0])
            
        # Display players
        for plajer in self.players:
            img = pygame.transform.rotate(plajer.img_player, -plajer.din)
            s = img.get_size()
            p = [plajer.pos[0] - 0.5 * s[0], plajer.pos[1] - 0.5 * s[1]]
            self.surface.blit(img, p)
            self.append_su_rects(su_rects, [p, s])
            p = [plajer.lpos[0] - 0.5 * s[0], plajer.lpos[1] - 0.5 * s[1]]
            self.append_su_rects(su_rects, [p, s])
        
        kill_anis = []
        for i in range(0, len(self.death_animations)):
            ani = self.death_animations[i]
            if ani.life <= 0:
                kill_anis.append(i)
        
        kill_anis.sort(reverse = 1)
        for i in kill_anis:
            ani = self.death_animations.pop(i)
            for rect in ani.rects:
                self.append_su_rects(su_rects, rect)
        
        for i in range(0, len(self.death_animations)):
            ani = self.death_animations[i]
            for rect in ani.get_rects():
                pygame.draw.rect(self.surface, ani.color, rect)
                self.append_su_rects(su_rects, rect)
            for rect in ani.lrects:
                self.append_su_rects(su_rects, rect)

    def append_su_rects(self, su_rects, rect):
        pad = 0.05 * (self.size_player[0] + self.size_player[1])
        p = [rect[0][0] - 0.5 * pad, rect[0][1] - 0.5 * pad]
        s = [rect[1][0] + pad, rect[1][1] + pad]
        su_rects.append([p, s])

    def ask_for_quit(self):
        if len(self.players) <= 1:
            if len(self.death_animations) <= 0:
                if len(self.players):
                    self.winner = self.players[0].player
                if self.death_wait_time <= 0:
                    return 1
                self.death_wait_time += -1
        return 0

class tron_player():
    def __init__(self, plajer, pos, din, delta_din, speed, size, trail_size, length, trail_rate, trail_accent, colorkey, team_count, team_colors):
        self.player = plajer
        self.opos = pos[:]
        self.odin = din
        self.delta_din = delta_din
        self.ospeed = speed
        self.size = [size, size]
        self.trail_size = trail_size
        self.kidth = 0.5 * self.trail_size[1]
        self.olength = length
        self.trail_rate = trail_rate
        if team_count > 0:
            self.trail_accent = team_colors[self.player.team - 1]
        else:
            self.trail_accent = trail_accent
        self.colorkey = colorkey
        self.restart()
        self.load_images()

    def restart(self):
        self.alive = 1
        self.color = self.player.base_color
        self.pos = self.opos[:]
        self.lpos = self.opos[:]
        self.din = self.odin
        self.speed = self.ospeed
        self.length = self.olength
        # 0: up, 1: right, 2: down, 3:left, backtrack ends the trail
        self.trail = self.length * [None]
        self.trail[-1] = [self.pos[:], self.din]
        self.trail_index = 0
        self.trail_cnt = 0
    
    def load_images(self):
        self.img_player = pygame.Surface(self.size)
        self.img_player.set_colorkey(self.colorkey)
        self.img_player.fill(self.trail_accent)
        self.img_player.fill(self.color, [[0.15 * self.size[0], 0.15 * self.size[1]], [0.7 * self.size[0], 0.7 * self.size[1]]])
        self.img_trail = pygame.Surface(self.trail_size)
        self.img_trail.set_colorkey(self.colorkey)
        self.img_trail.fill(self.trail_accent)
        self.img_trail.fill(self.color, [[0, 0.2 * self.trail_size[1]], [self.trail_size[0], 0.6 * self.trail_size[1]]])

    def move(self):
        self.lpos = self.pos[:]
        new_dir = [0, 0]
        controls = self.player.controls
        if controls['left'][-1]:
            new_dir[0] += -1
        if controls['right'][-1]:
            new_dir[0] += 1
        if controls['up'][-1]:
            new_dir[1] += -1
        if controls['down'][-1]:
            new_dir[1] += 1
        # Compare the new and old din and find how far to move considering delta dins
        if new_dir != [0, 0]:
            new_din = simple_vector_angle(new_dir)
            self.new_din = new_din
            if (new_din - self.din) % 360 < 180:
                # Add
                if (new_din - self.din) % 360 < self.delta_din:
                    self.din = new_din
                else:
                    self.din += self.delta_din
            else:
                # Subtract
                if 360 - ((new_din - self.din) % 360) < self.delta_din:
                    self.din = new_din
                else:
                    self.din -= self.delta_din
        else:
            self.new_din = 0
        
        # Move forward in that direction
        self.pos[0] += self.speed * math.cos(self.din * math.pi / 180)
        self.pos[1] += self.speed * math.sin(self.din * math.pi / 180)

        # Create a new trail and delete the oldest one
        if self.trail_cnt >= self.trail_rate:
            self.trail[self.trail_index] = [self.pos[:], self.din]
            self.trail_index = (self.trail_index + 1) % self.length
            self.trail_cnt = 0
        else:
            self.trail_cnt += 1

def in_rect(point, rect_pos, rect_size, lwl = None):
    if lwl != None:
        if lwl.horizontal_looping:
            p = [rect_pos[0] - lwl.size[0], rect_pos[1]]
            if in_rect(point, p, rect_size):
                return 1
            p = [rect_pos[0] + lwl.size[0], rect_pos[1]]
            if in_rect(point, p, rect_size):
                return 1
        if lwl.vertical_looping:
            p = [rect_pos[0], rect_pos[1] - lwl.size[1]]
            if in_rect(point, p, rect_size):
                return 1
            p = [rect_pos[0], rect_pos[1] + lwl.size[1]]
            if in_rect(point, p, rect_size):
                return 1
        if lwl.horizontal_looping and lwl.vertical_looping:
            p = [rect_pos[0] - lwl.size[0], rect_pos[1] - lwl.size[1]]
            if in_rect(point, p, rect_size):
                return 1
            p = [rect_pos[0] - lwl.size[0], rect_pos[1] + lwl.size[1]]
            if in_rect(point, p, rect_size):
                return 1
            p = [rect_pos[0] + lwl.size[0], rect_pos[1] - lwl.size[1]]
            if in_rect(point, p, rect_size):
                return 1
            p = [rect_pos[0] + lwl.size[0], rect_pos[1] + lwl.size[1]]
            if in_rect(point, p, rect_size):
                return 1
    for i in range(0, len(point)):
        if point[i] < rect_pos[i] or point[i] > rect_pos[i] + rect_size[i]:
            return 0
    return 1

def rect_overlap(p1, s1, v1, p2, s2, v2 = [0, 0], inclusive = 1, override = 0, lwl = None):
    if lwl:
        overlaps = []
        grid = [[-1, -1], [0, -1], [1, -1],
                [-1, 0], [0, 0], [1, 0],
                [-1, 1], [0, 1], [1, 1]]
        if lwl.horizontal_looping and lwl.vertical_looping:
            grid_indeces = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        elif lwl.horizontal_looping:
            grid_indeces = [3, 4, 5]
        elif lwl.vertical_looping:
            grid_indeces = [1, 4, 7]
        else:
            grid_indeces = [4]
        base_p2 = p2
        for index in grid_indeces:
            grid_multiplier = grid[index]
            p2 = [base_p2[0] + grid_multiplier[0] * lwl.size[0], base_p2[1] + grid_multiplier[1] * lwl.size[1]]
            overlap = [0, 0]
            for i in range(0, 2):
                if inclusive:
                    if p1[i] + s1[i] >= p2[i]:
                        if p1[i] <= p2[i] + s2[i]:
                            if p1[i] - v1[i] <= p2[i] - v2[i] or override:
                                overlap[i] = p2[i] - p1[i] - s1[i]
                            else:
                                overlap[i] = p2[i] + s2[i] - p1[i]
                else:
                    if p1[i] + s1[i] > p2[i]:
                        if p1[i] < p2[i] + s2[i]:
                            if p1[i] - v1[i] < p2[i] - v2[i] or override:
                                overlap[i] = p2[i] - p1[i] - s1[i]
                            else:
                                overlap[i] = p2[i] + s2[i] - p1[i]
            if (overlap[0] == 0) or (overlap[1] == 0):
                overlap = [0, 0]
            overlaps.append(overlap)
        return biggest_vector(overlaps)
    overlap = [0, 0]
    for i in range(0, 2):
        if inclusive:
            if p1[i] + s1[i] >= p2[i]:
                if p1[i] <= p2[i] + s2[i]:
                    if p1[i] - v1[i] <= p2[i] - v2[i] or override:
                        overlap[i] = p2[i] - p1[i] - s1[i]
                    else:
                        overlap[i] = p2[i] + s2[i] - p1[i]
        else:
            if p1[i] + s1[i] > p2[i]:
                if p1[i] < p2[i] + s2[i]:
                    if p1[i] - v1[i] < p2[i] - v2[i] or override:
                        overlap[i] = p2[i] - p1[i] - s1[i]
                    else:
                        overlap[i] = p2[i] + s2[i] - p1[i]
    if (overlap[0] == 0) or (overlap[1] == 0):
        overlap = [0, 0]
    return overlap

def find_wrapped_point(point, size, lvl, i = -1):
    wrapped = [0, 0]
    if i == -1:
        if lvl.horizontal_looping:
            if lvl.size[0] != 0:
                if point[0] < 0:
                    wrapped[0] = -1
                elif point[0] >= lvl.size[0]:
                    wrapped[0] = 1
                point[0] %= lvl.size[0]
        else:
            if point[0] < -size[0] * lvl.side_wall_depth * 0.01:
                point[0] = -size[0] * lvl.side_wall_depth * 0.01
            elif point[0] > lvl.size[0] + size[0] * (lvl.side_wall_depth * 0.01 - 1):
                point[0] = lvl.size[0] + size[0] * (lvl.side_wall_depth * 0.01 - 1)
        if lvl.vertical_looping:
            if lvl.size[1] != 0:
                if point[1] < -size[1]:
                    wrapped[1] = -1
                elif point[1] >= lvl.size[1]:
                    wrapped[1] = 1
                point[1] %= lvl.size[1]
    elif i == 0:
        if lvl.horizontal_looping:
            if lvl.size[0] != 0:
                if point < 0:
                    wrapped[0] = -1
                elif point >= lvl.size[0]:
                    wrapped[0] = 1
                point %= lvl.size[0]
            else:
                if point < -size[0] * lvl.side_wall_depth * 0.01:
                    point = -size[0] * lvl.side_wall_depth * 0.01
                elif point > lvl.size[0] + size[0] * lvl.side_wall_depth * 0.01:
                    point = lvl.size[0] + size[0] * lvl.side_wall_depth * 0.01
    elif i == 1:
        if lvl.vertical_looping:
            if lvl.size[1] != 0:
                if point < 0:
                    wrapped[1] = -1
                elif point >= lvl.size[1]:
                    wrapped[1] = 1
                point %= lvl.size[1]
    return [point, wrapped]

def compare_wrapped(p1, s1, p2, s2, lvl, i, inclusive = 0, precision = 10000000):
    if inclusive:
        if round(precision * (p1[i] + s1[i])) / precision >= round(precision * p2[i]) / precision:
            if round(precision * (p2[i] + s2[i])) / precision >= round(precision * p1[i]) / precision:
                return 1
        if (round(precision * (p1[i] + s1[i])) / precision >= lvl.size[i]) or (round(precision * (p2[i] + s2[i])) / precision >= lvl.size[i]):
            if ((i == 0) and lvl.horizontal_looping) or ((i == 1) and lvl.vertical_looping):
                if round(precision * (p1[i] + s1[i])) / precision - lvl.size[i] >= round(precision * p2[i]) / precision:
                    if round(precision * (p2[i] + s2[i])) / precision >= round(precision * (p1[i])) / precision - lvl.size[i]:
                        return 1
                if round(precision * (p1[i] + s1[i])) / precision + lvl.size[i] >= round(precision * p2[i]) / precision:
                    if round(precision * (p2[i] + s2[i])) / precision >= round(precision * (p1[i])) / precision + lvl.size[i]:
                        return 1
    else:
        if round(precision * (p1[i] + s1[i])) / precision > round(precision * p2[i]) / precision:
            if round(precision * (p2[i] + s2[i])) / precision > round(precision * p1[i]) / precision:
                return 1
        if (round(precision * (p1[i] + s1[i])) / precision > lvl.size[i]) or (round(precision * (p2[i] + s2[i])) / precision > lvl.size[i]):
            if ((i == 0) and lvl.horizontal_looping) or ((i == 1) and lvl.vertical_looping):
                if round(precision * (p1[i] + s1[i])) / precision - lvl.size[i] > round(precision * p2[i]) / precision:
                    if round(precision * (p2[i] + s2[i])) / precision > round(precision * (p1[i])) / precision - lvl.size[i]:
                        return 1
                if round(precision * (p1[i] + s1[i])) / precision + lvl.size[i] > round(precision * p2[i]) / precision:
                    if round(precision * (p2[i] + s2[i])) / precision > round(precision * p1[i]) / precision + lvl.size[i]:
                        return 1
    return 0

def check_collision_direction(p1, s1, v1, p2, s2, lvl):
    if v1[1] == 0:
        return 0
    elif v1[1] > 0:
        dy = (p2[1] - (p1[1] + s1[1]) + 0.5 * lvl.size[1]) % (lvl.size[1]) - 0.5 * lvl.size[1]
    else:
        dy = (p1[1] - (p2[1] + s2[1]) + 0.5 * lvl.size[1]) % (lvl.size[1]) - 0.5 * lvl.size[1]
    if v1[0] == 0:
        return 1
    elif v1[0] > 0:
        dx = (p2[0] - (p1[0] + s1[0]) + 0.5 * lvl.size[0]) % (lvl.size[0]) - 0.5 * lvl.size[0]
    else:
        dx = (p1[0] - (p2[0] + s2[0]) + 0.5 * lvl.size[0]) % (lvl.size[0]) - 0.5 * lvl.size[0]
    if dx == 0:
        return 0
    vpdx = v1[0] / dx
    if vpdx < 0:
        return 1
    if dy == 0:
        return 1
    vpdy = v1[1] / dy
    if vpdy < 0:
        return 0
    if vpdx < 0:
        return 1
    return vpdx < vpdy

def findxy(string, refrence_size = [0, 0], refrence_pos = [0, 0], self_size = [0, 0], is_int = 0):
    # Find [x, y] in 'word = [jxx, jxy]'
    # j = r,d: right/down justified
    # j = l,u: left/up justified
    # j = c: centered justified
    # 'x' means relative to refrence
    string = string.split('[')[-1]
    string = string.split(']')[0]
    string = string.split(',')
    xy = [0, 0]
    match = -1
    for i in range(0, 2):
        if (string[i][0] == 'l') or (string[i][0] == 'u'):
            if (string[i][1] == 'x'):
                xy[i] = refrence_pos[i] + refrence_size[i] * float(string[i][2:])
            else:
                xy[i] = float(string[i][1:])
        elif string[i][0] == 'c':
            if (string[i][1] == 'x'):
                xy[i] = refrence_pos[i] + refrence_size[i] * float(string[i][2:]) - 0.5 * self_size[i]
            else:
                xy[i] = float(string[i][1:]) - 0.5 * self_size[i]
        elif (string[i][0] == 'r') or (string[i][0] == 'd'):
            if (string[i][1] == 'x'):
                xy[i] = refrence_pos[i] + refrence_size[i] * float(string[i][2:]) - self_size[i]
            else:
                xy[i] = float(string[i][1:]) - self_size[i]
        elif string[i][0] == 'x':
            xy[i] = refrence_size[i] * float(string[i][1:])
        elif string[i][0] == 'm':
            match = i
        else:
            xy[i] = float(string[i])
    if match != -1:
        xy[match] = xy[not match]
    if is_int:
        xy = [int(xy[0]), int(xy[1])]
    return xy

def findx(string, refrence_size = 0):
    # Find x 'word = xx'
    # 'x' means relative to refrence
    if string[0] == 'x':
        return refrence_size * float(string[1:])
    return float(string)

def point2size(p1, p2, rounding = 0):
    if rounding:
        p3 = [round(min(p1[0], p2[0]) * rounding) / rounding, round(min(p1[1], p2[1]) * rounding) / rounding]
        size = [round(abs(p1[0] - p2[0]) * rounding) / rounding, round(abs(p1[1] - p2[1]) * rounding) / rounding]
        if rounding == 1:
            p3 = [int(p3[0]), int(p3[1])]
            size = [int(size[0]), int(size[1])]
        return [p3, size]
    else:
        p3 = [min(p1[0], p2[0]), min(p1[1], p2[1])]
        size = [abs(p1[0] - p2[0]), abs(p1[1] - p2[1])]
        return [p3, size]

def reflect_rect(rect, display_size):
    return [[display_size[0] - rect[0][0] - rect[1][0], rect[0][1]], rect[1]]

def has_greater_magnitude(given_list, value):
    if len(given_list) == 0:
        return 1
    for item in given_list:
        if abs(value) > abs(item):
            return 1
    return 0

def biggest_vector(vectors):
    if len(vectors) == 0:
        return [0, 0]
    index = 0
    mak = 0
    for i in range(0, len(vectors)):
        val = (vectors[i][0] ** 2 + vectors[i][1] ** 2) ** 0.5
        if val > mak:
            mak = val
            index = i
    return vectors[index]

def keep_within(input_list, limit1, limit2):
    if limit1 >= limit2:
        upper_limit = limit1
        lower_limit = limit2
    else:
        upper_limit = limit2
        lower_limit = limit1
    if type(input_list) == type(list()):
        return_list = [0] * len(input_list)
        for i in range(0, len(input_list)):
            if input_list[i] > upper_limit:
                return_list[i] = upper_limit
            elif input_list[i] < lower_limit:
                return_list[i] = lower_limit
            else:
                return_list[i] = input_list[i]
        return return_list
    else:
        if input_list > upper_limit:
            return_value = upper_limit
        elif input_list < lower_limit:
            return_value = lower_limit
        else:
            return_value = input_list
        return return_value

def sign(num):
    if num < 0:
        return -1
    return 1

def shift_chars(input_string, shift_amount):
    hex_string = input_string.encode('utf-16').hex()
    total_shift = 0
    for i in range(0, len(hex_string)):
        total_shift += shift_amount * (16 ** i)
    return bytes.fromhex(hex((int(hex_string, 16) + total_shift) % (16 ** len(hex_string)))[2:]).decode('utf-16')[1:]

def distance(vector_1, vector_2, lvl = None):
    total = 0
    if lvl:
        for i, lvl_size in enumerate(lvl.size):
            dd = abs(vector_1[i] - vector_2[i])
            if ((i == 0) and lvl.horizontal_looping) or ((i == 1) and lvl.vertical_looping):
                if dd > 0.5 * lvl_size:
                    dd= lvl_size - dd
            total += dd ** 2
        return (total) ** 0.5
    else:
        for i in range(0, min([len(vector_1), len(vector_2)])):
            total += (vector_2[i] - vector_1[i]) ** 2
        return (total) ** 0.5

def magnitude(vector):
    total = 0
    for i in range(0, len(vector)):
        total += vector[i] ** 2
    return (total) ** 0.5

def simple_vector_angle(vector):
    if vector[0] == -1:
        if vector[1] == -1:
            return 225
        if vector[1] == 0:
            return 180
        if vector[1] == 1:
            return 135
    if vector[0] == 0:
        if vector[1] == -1:
            return 270
        if vector[1] == 1:
            return 90
    if vector[0] == 1:
        if vector[1] == -1:
            return 315
        if vector[1] == 0:
            return 0
        if vector[1] == 1:
            return 45

def remove_redundancy(input_list):
    return_list = []
    for entry in input_list:
        if not return_list.count(entry):
            return_list.append(entry)
    return return_list

def randomize_list(input_list):
    return_list = []
    while len(input_list):
        return_list.append(input_list.pop(random.randint(0, len(input_list) - 1)))
    return return_list

def unbiased_smallest(input_list):
    if len(input_list):
        smallest = []
        value = None
        for i in range(0, len(input_list)):
            if (value == None) or (input_list[i] < value):
                value = input_list[i]
                smallest = [i]
            elif input_list[i] == value:
                smallest.append(i)
        return smallest[random.randint(0, len(smallest) - 1)]
    return None