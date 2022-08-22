import pygame, os, time, random

class game():
    def __init__(self):
        pygame.init()
        self.running = 1
        self.mode = 'page'

        pygame.display.set_caption('squish')
        self.display_info = pygame.display.Info()
        self.display_size = [self.display_info.current_w, self.display_info.current_h]
        self.display = pygame.display.set_mode(self.display_size)
        self.surface = pygame.Surface(self.display_size)
        self.clock = pygame.time.Clock()
        self.tick = 50

        self.reset_joysticks()
        self.reset_mapping()

        self.cwd = os.getcwd()
        pgd = os.path.join(self.cwd, 'pages')
        self.pages = {}
        for pg in os.listdir(pgd):
            file = open(os.path.join(pgd, pg), encoding = 'utf-8')
            self.pages[pg.replace('.txt', '')] = page(file.readlines(), self.display_size)
            file.close()

        self.page = 'main'
        self.next_page = 'main'
        self.reset_menu_navigation()
        self.show_fps = False

        self.reset_editor_tools()

        self.level_directory = os.path.join(self.cwd, 'levels')
        self.load_levels()
        self.level = ''

        self.shield_color = 0x010101
        file = open(os.path.join(self.cwd, 'player_data.txt'), encoding = 'utf-8')
        self.load_player_data(file)
        file.close()

        self.valid_name_inputs = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789'
        self.valid_int_inputs = '0123456789'
        self.valid_float_inputs = '.0123456789'
        self.valid_hex_inputs = '0123456789abcdefABCDEF'
        self.valid_inputs = ''
        self.text_input = ''
        self.text_last_input = ''
        self.text_input_action = -1

        self.kill_width = 0.2
        self.winner_index = 0

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
        pygame.mouse.set_visible(1)

    def reset_joysticks(self):
        self.joystick_threshold = 0.85
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
                if abs(joy.get_axis(axis)) >= self.joystick_threshold * 0.5:
                    no_joy = 0
            for axis in range(joy.get_numaxes() - 2, joy.get_numaxes()):
                if joy.get_axis(axis) >= self.joystick_threshold * 0.5:
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
                    self.new_controls[self.current_map] = [-1, event.key, 0]
                    self.has_mapped = 1
                    break
            elif event.type == pygame.JOYBUTTONDOWN:
                self.new_controls[self.current_map] = [event.joy, 'button', event.button, 1, 0]
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
                    self.new_controls[self.current_map] = [event.joy, 'axis', event.axis, direction, 0]
                    self.has_mapped = 1
                    self.do_joy = 0
                    break
            elif event.type == pygame.JOYHATMOTION:
                if self.do_hat and ((event.value[0] != 0) ^ (event.value[1] != 0)):
                    self.new_controls[self.current_map] = [event.joy, 'hat', event.hat, int(event.value), 0]
                    self.has_mapped = 1
                    self.do_hat = 0
                    break

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
    
    def draw_alpha(self, color, alpha):
        alpha_surface = pygame.Surface(self.display_size)
        alpha_surface.fill(color)
        alpha_surface.set_alpha(alpha)
        self.surface.blit(alpha_surface, [0, 0])

    def get_page_inputs(self):
        self.mouse_moved = not ((0,0) == pygame.mouse.get_rel())
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_last_lmb = self.mouse_lmb
        self.mouse_lmb = pygame.mouse.get_pressed()[0]
        self.mouse_wheel = 0
        if not self.mapping:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = 0
                if event.type == pygame.MOUSEWHEEL:
                    self.mouse_wheel = event.y * self.scroll_speed
                if (event.type == pygame.KEYDOWN) or (event.type == pygame.KEYUP):
                    key_direction = (event.type == pygame.KEYDOWN)
                    if event.key == pygame.K_UP:
                        self.menu_controls['up'] = key_direction
                        self.menu_input_delay_index[1] = 0
                    elif event.key == pygame.K_DOWN:
                        self.menu_controls['down'] = key_direction
                        self.menu_input_delay_index[1] = 0
                    elif event.key == pygame.K_LEFT:
                        self.menu_controls['left'] = key_direction
                        self.menu_input_delay_index[0] = 0
                    elif event.key == pygame.K_RIGHT:
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
                if (event.type == pygame.JOYDEVICEADDED) or (event.type == pygame.JOYDEVICEREMOVED):
                    self.reset_joysticks()

            for kontroller in self.controllers:
                kontroller.check_inputs(self.menu_controls, self.menu_input_delay_index, self.menu_controls['page_entrance'])
                
        else:
            self.map_event()

    def run_page(self):
        if self.menu_controls['page_entrance']:
            self.reset_menu_navigation()
            self.find_list_buttons()
            for i in range(0, len(self.pages[self.page].lists)):
                self.pages[self.page].lists[i].scroll_value = 0
            for control in self.pages[self.page].controls:
                if control.trigger == 'page_entrance':
                    self.do_actions(control.actions)

        for control in self.pages[self.page].controls:
            if control.trigger == 'continual_early':
                self.do_actions(control.actions)

        self.last_cursor = [self.cursor[0], self.cursor[1]]

        for block in self.pages[self.page].blocks:
            if block.dynamic_color:
                if block.dynamic_color[0] == 'level':
                    if block.dynamic_color[1] == 'background_color':
                        block.color = self.levels[self.level].background_color
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
                    variable_text = block.text.format(self.current_map.capitalize()[0:block.text_variable_char_limit])
                elif block.text_variable == 'winner':
                    if self.winner_index < len(self.players):
                        winner_name = self.players[self.winner_index].name
                    if len(winner_name) > 0:
                        if winner_name[0].isupper():
                            variable_text = block.text.format(winner_name[0:block.text_variable_char_limit] + ' W')
                        else:
                            variable_text = block.text.format(winner_name[0:block.text_variable_char_limit] + ' w')
                [block.text_image, new_text_image_size] = text2img(variable_text, block.text_color, block.text_font, block.text_size, block.text_bold)
            if block.color != -1:
                block_surface = pygame.Surface(block.size)
                block_surface.fill(block.color)
                if block.alpha != 255:
                    block_surface.set_alpha(block.alpha)
                self.surface.blit(block_surface, block.pos)
            if block.text_image != 0:
                if block.text_dynamic_pos:
                    block.text_pos = findxy(block.text_pos_string, block.size, block.pos, new_text_image_size)
                self.surface.blit(block.text_image, block.text_pos)
        
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
                if in_rect(self.mouse_pos, button.pos, button.size):
                    if self.mouse_moved:
                        do_menu_navigation = [0, 0]
                        self.cursor = [button.button_pos[0], button.button_pos[1]]
                    if self.mouse_lmb and not self.mouse_last_lmb:
                        do_menu_navigation = [0, 0]
                        self.cursor = [button.button_pos[0], button.button_pos[1]]
                        self.menu_controls['select'] = 1
            
            for lisk in self.pages[self.page].lists:
                if lisk.selectable:
                    if in_rect(self.mouse_pos, lisk.pos, lisk.size):
                        list_length = len(self.players) * (lisk.type == 'player') + len(self.levels) * (lisk.type == 'level')
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
            list_length = len(self.players) * ((lisk.type == 'player') or (lisk.type == 'score')) + len(self.levels) * (lisk.type == 'level')
            if self.mouse_wheel and not lisk.only_last:
                lisk.scroll(self.mouse_wheel, list_length)
            if lisk.selectable:
                if self.cursor[0] == lisk.select_pos[0]:
                    if self.cursor[1] >= lisk.select_pos[1]:
                        if self.cursor[1] < lisk.select_pos[1] + list_length:
                            self.cursor_on_list = 1
                            if self.cursor != self.last_cursor:
                                selected_corner = (self.cursor[1] - lisk.select_pos[1]) * (lisk.entry_size[1] + lisk.entry_spacing) + lisk.scroll_value
                                if selected_corner + lisk.entry_size[1] > lisk.size[1]:
                                    lisk.scroll(-1 * (selected_corner - lisk.size[1] + lisk.entry_size[1]), list_length)
                                elif selected_corner < 0:
                                    lisk.scroll(-1 * selected_corner, list_length)
                            if self.menu_controls['select']:
                                self.menu_controls['select'] = 0
                                self.do_actions(lisk.actions, self.cursor[1] - lisk.select_pos[1])
            list_surface = pygame.Surface(lisk.size)
            list_surface.fill(lisk.color)
            list_length = len(self.players) * ((lisk.type == 'player') or (lisk.type == 'score')) + len(self.levels) * (lisk.type == 'level')
            for i in range((lisk.only_last) * (list_length - 1), list_length):
                entry_surface = pygame.Surface(lisk.entry_size)
                entry_surface.fill(lisk.entry_color)
                if lisk.selectable:
                    if self.cursor == [lisk.select_pos[0], lisk.select_pos[1] + i]:
                        entry_surface.fill(lisk.select_color)
                if (lisk.type == 'player') or (lisk.type == 'score'):
                    entry = self.players[i]
                    pygame.draw.rect(entry_surface, entry.base_color, [lisk.image_pos, lisk.image_size])
                    if lisk.type == 'score':
                        score_image = text2img(str(entry.wins), lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)
                        score_image_pos = [lisk.wins_pos[0] - score_image[1][0] / 2, lisk.wins_pos[1]]
                        entry_surface.blit(score_image[0], score_image_pos)
                        score_image = text2img(str(entry.kills), lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)
                        score_image_pos = [lisk.kills_pos[0] - score_image[1][0] / 2, lisk.kills_pos[1]]
                        entry_surface.blit(score_image[0], score_image_pos)
                elif lisk.type == 'level':
                    entry = self.levels[[*self.levels][i]]
                    pygame.draw.rect(entry_surface, lisk.frame_color, [lisk.frame_pos, lisk.frame_size])
                    entry_surface.blit(pygame.transform.scale(entry.thumbnail, lisk.image_size), lisk.image_pos)
                if lisk.only_last:
                    i = 0
                if lisk.text_limit == None:
                    entry_surface.blit(text2img(entry.name, lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)[0], lisk.text_pos)
                else:
                    text_surface = pygame.Surface(lisk.text_limit, pygame.SRCALPHA)
                    text_surface.blit(text2img(entry.name, lisk.text_color, lisk.text_font, lisk.text_size, lisk.text_bold)[0], [0, 0])
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
                else:
                    pygame.draw.rect(self.surface, button.active_color, [button.pos, button.size])
            elif button.color != -1:
                pygame.draw.rect(self.surface, button.color, [button.pos, button.size])
            if button.text_image != 0:
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
                                        button.text_input = '0.0'
                                    else:
                                        button.text_input = str(self.edited_block.pos[0])
                                elif action[3] == 'y_pos':
                                    if self.text_input_action == action:
                                        button.text_input = self.text_input
                                    elif self.edited_block.pos[1] == 0:
                                        button.text_input = '0.0'
                                    else:
                                        button.text_input = str(self.edited_block.pos[1])
                                elif action[3] == 'x_size':
                                    if self.text_input_action == action:
                                        button.text_input = self.text_input
                                    elif self.edited_block.size[0] == 0:
                                        button.text_input = '0.0'
                                    else:
                                        button.text_input = str(self.edited_block.size[0])
                                elif action[3] == 'y_size':
                                    if self.text_input_action == action:
                                        button.text_input = self.text_input
                                    elif self.edited_block.size[1] == 0:
                                        button.text_input = '0.0'
                                    else:
                                        button.text_input = str(self.edited_block.size[1])
                            elif action[2] == 'player':
                                if action[3] == 'x_pos':
                                    if self.text_input_action == action:
                                        button.text_input = self.text_input
                                    elif self.edited_player_pos[0] == 0:
                                        button.text_input = '0.0'
                                    else:
                                        button.text_input = str(self.edited_player_pos[0])
                                elif action[3] == 'y_pos':
                                    if self.text_input_action == action:
                                        button.text_input = self.text_input
                                    elif self.edited_player_pos[1] == 0:
                                        button.text_input = '0.0'
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
                        elif action[1] == 'game':
                            if action[2] == 'show_fps':
                                button.text_input = str(self.show_fps)
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
                    input_surface.blit(text2img(button.text + button.text_input, button.text_color, button.text_font, button.text_size, button.text_bold)[0], [0, 0])
                else:
                    input_surface.blit(button.text_image, [0, 0])
                self.surface.blit(input_surface, button.text_pos)

        for control in self.pages[self.page].controls:
            if control.trigger != 'page_entrance' and control.trigger != 'continual_early':
                if self.menu_controls[control.trigger]:
                    self.do_actions(control.actions)

    def load_levels(self):
        self.levels = {}
        for lv in os.listdir(self.level_directory):
            file = open(os.path.join(self.level_directory, lv), encoding = 'utf-8')
            self.levels[lv.replace('.txt', '')] = level(file.readlines(), lv.replace('.txt', ''))
            file.close()

    def initialize_level(self):
        for i in range(0, len(self.players)):
            lvl = self.levels[self.level]
            if i < len(lvl.player_poses):
                player_pos = lvl.player_poses[i]
            else:
                player_pos = [3 * (i - len(lvl.player_poses)) * lvl.player_size[0], 0]
            self.players[i].soft_reset(player_pos, lvl.player_size, lvl.player_gravity, lvl.player_jump_strength, lvl.player_vel_terminal, lvl.player_vel_delta, lvl.player_shield_health_base, lvl.player_shield_regen)
        pygame.mouse.set_visible(0)

    def get_level_inputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = 0
            if ((event.type == pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE)) or ((event.type == pygame.JOYBUTTONDOWN) and (event.button == pygame.CONTROLLER_BUTTON_BACK)):
                self.do_actions([['goto', 'pause']])
            if (event.type == pygame.JOYDEVICEADDED) or (event.type == pygame.JOYDEVICEREMOVED):
                self.reset_joysticks()

        key = pygame.key.get_pressed()
        for plajer in self.players:
            for control_key in plajer.controls:
                control = plajer.controls[control_key][:]
                if control[0] == -1:
                    plajer.controls[control_key][-1] = key[control[1]]
                if len(self.controllers) > 0:
                    if control[0] >= len(self.controllers):
                        control[0] %= len(self.controllers)
                    if control[0] != -1:
                        if control[1] == 'button':
                            plajer.controls[control_key][-1] = self.joysticks[control[0]].get_button(control[2])
                        elif control[1] == 'axis':
                            plajer.controls[control_key][-1] = (control[3] * self.joysticks[control[0]].get_axis(control[2]) >= self.joystick_threshold)
                        elif control[1] == 'hat':
                            plajer.controls[control_key][-1] = (self.joysticks[control[0]].get_hat(control[2]) == control[3])

    def run_level(self):
        lvl = self.levels[self.level]
        lvl.surface.fill(lvl.background_color)

        if lvl.horizontal_looping:
            #edge_surface = pygame.Surface([lvl.size[0] * 0.01, lvl.size[1]])
            #edge_surface.fill(0x10a0ff)
            #edge_surface.set_alpha(250)
            #lvl.surface.blit(edge_surface, [-lvl.size[0] * 0.007, 0])
            #edge_surface = pygame.Surface([lvl.size[0] * 0.01, lvl.size[1]])
            #edge_surface.fill(0x10a0ff)
            #edge_surface.set_alpha(250)
            #lvl.surface.blit(edge_surface, [lvl.size[0] * 0.997, 0])
            pygame.draw.rect(lvl.surface, 0x10a0ff, [[-lvl.size[0] * 0.007, 0], [lvl.size[0] * 0.01, lvl.size[1]]])
            pygame.draw.rect(lvl.surface, 0x10a0ff, [[lvl.size[0] * 0.997, 0], [lvl.size[0] * 0.01, lvl.size[1]]])
        if not lvl.vertical_looping:
            #edge_surface = pygame.Surface([lvl.size[0], lvl.size[1] * 0.01])
            #edge_surface.fill(0xff0000)
            #edge_surface.set_alpha(250)
            #lvl.surface.blit(edge_surface, [0, lvl.size[1] * 0.996])
            pygame.draw.rect(lvl.surface, 0xff0000, [[0, lvl.size[1] * 0.996], [lvl.size[0], lvl.size[1] * 0.01]])
            for plajer in self.players:
                if plajer.alive and (plajer.pos[1] >= lvl.size[1]):
                    plajer.alive = 0

        for i in range(0, len(self.players)):
            if self.players[i].alive:
                self.players[i].check_kill(lvl, self.players, self.kill_width, self.shield_color, i)
                self.players[i].check_ground(lvl, self.players, i)
        
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if plajer.alive:
                plajer.lpos = plajer.pos
                plajer.lvel = plajer.vel

                plajer.vel_desired = [(plajer.controls['right'][-1] - plajer.controls['left'][-1]) * plajer.vel_terminal[0], plajer.gravity]
                for ii in range(0, 2):
                    if plajer.vel[ii] < plajer.vel_desired[ii]:
                        if plajer.vel[ii] + plajer.vel_delta[ii] > plajer.vel_desired[ii]:
                            plajer.vel[ii] = plajer.vel_desired[ii]
                        else:
                            plajer.vel[ii] += plajer.vel_delta[ii]
                    elif plajer.vel[ii] > plajer.vel_desired[ii]:
                        if plajer.vel[ii] - plajer.vel_delta[ii] < plajer.vel_desired[ii]:
                            plajer.vel[ii] = plajer.vel_desired[ii]
                        else:
                            plajer.vel[ii] -= plajer.vel_delta[ii]
                    if plajer.vel[ii] > plajer.vel_terminal[ii]:
                        plajer.vel[ii] = plajer.vel_terminal[ii]
                    if plajer.vel[ii] < -plajer.vel_terminal[ii]:
                        plajer.vel[ii] = -plajer.vel_terminal[ii]
                if plajer.controls['jump'][-1] and plajer.on_ground:
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

                new_point = [plajer.pos[0] + plajer.vel[0], plajer.pos[1] + plajer.vel[1]]
                result = find_wrapped_point(new_point, plajer.size, lvl)
                plajer.pos = result[0]
                plajer.update_vel(lvl)

                for block in lvl.blocks:
                    plajer.block_collision(block, lvl)
                
                for ii in range(0, len(self.players)):
                    # TODO: add in player pushing
                    if i != ii:
                        plajer.player_collision(self.players, lvl, [i, ii])

        for block in lvl.blocks:
            pygame.draw.rect(lvl.surface, block.color, [block.pos, block.size])
        
        player_cnt = 0
        self.winner_index = 0
        for i in range(0, len(self.players)):
            plajer = self.players[i]
            if plajer.alive:
                player_cnt += 1
                self.winner_index = i
                pygame.draw.rect(lvl.surface, plajer.color, [plajer.pos, plajer.size])
                if lvl.horizontal_looping:
                    pos = [plajer.pos[0] - lvl.size[0], plajer.pos[1]]
                    pygame.draw.rect(lvl.surface, plajer.color, [pos, plajer.size])
                if lvl.vertical_looping:
                    pos = [plajer.pos[0], plajer.pos[1] - lvl.size[1]]
                    pygame.draw.rect(lvl.surface, plajer.color, [pos, plajer.size])
                if lvl.horizontal_looping and lvl.vertical_looping:
                    pos = [plajer.pos[0] - lvl.size[0], plajer.pos[1] - lvl.size[1]]
                    pygame.draw.rect(lvl.surface, plajer.color, [pos, plajer.size])
        
        if player_cnt <= 1:
            if len(self.players) == 0:
                self.do_actions([['goto', 'no_players']])
            elif len(self.players) == 1:
                self.do_actions([['goto', 'single_player']])
            else:
                self.players[self.winner_index].wins += 1
                self.do_actions([['goto', 'end_game']])
        
        self.surface.blit(pygame.transform.scale(lvl.surface, self.display_size), [0, 0])

    def do_actions(self, actions, index = -1):
        for action in actions:
            if action[0] == 'quit':
                self.running = 0
            elif action[0] == 'goto':
                self.mode = 'page'
                self.next_page = action[1]
                self.menu_controls['page_entrance'] = 1
            elif action[0] == 'select_level':
                if action[1] == 'from_list':
                    if len(self.levels) > index:
                        self.level = [*self.levels][index]
            elif action[0] == 'load_levels':
                self.load_levels()
            elif action[0] == 'save_level':
                self.levels[self.level].export_level_file()
            elif action[0] == 'play_level':
                if action[1] == 'from_list':
                    if len(self.levels) > index:
                        self.level = [*self.levels][index]
                elif action[1] == 'random':
                    if len(self.levels) > 0:
                        i = random.Random().randint(0, len(self.levels) - 1)
                        self.level = [*self.levels][i]
                self.mode = 'in_game'
                self.initialize_level()
            elif action[0] == 'resume_level':
                self.mode = 'in_game'
                pygame.mouse.set_visible(0)
            elif action[0] == 'reset_editor':
                self.reset_editor_tools()
            elif action[0] == 'edit_level':
                self.mode = 'editor'
                self.soft_reset_editor_tools()
            elif action[0] == 'editor_display_level':
                self.editor_display_level()
            elif action[0] == 'update_edited_block':
                self.levels[self.level].blocks[self.edit_index] = self.edited_block
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
            elif action[0] == 'update_controllers':
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
                elif action[1] == 'game':
                    if action[2] == 'show_fps':
                        self.show_fps = not self.show_fps
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

    def apply_text_input(self, text):
        if self.text_input_action != -1:
            # HERE 2
            if self.text_input_action[1] == 'level':
                if self.text_input_action[2] == 'name':
                    self.levels[self.level].name = text
                elif self.text_input_action[2] == 'width':
                    if text == '':
                        self.levels[self.level].size[0] = 0
                    else:
                        self.levels[self.level].size[0] = int(text)
                elif self.text_input_action[2] == 'height':
                    if text == '':
                        self.levels[self.level].size[1] = 0
                    else:
                        self.levels[self.level].size[1] = int(text)
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
                            self.edited_block.pos[0] = float(text)
                        else:
                            self.edited_block.pos[0] = 0.0
                    elif self.text_input_action[3] == 'y_pos':
                        if text:
                            self.edited_block.pos[1] = float(text)
                        else:
                            self.edited_block.pos[1] = 0.0
                    elif self.text_input_action[3] == 'x_size':
                        if text:
                            self.edited_block.size[0] = float(text)
                        else:
                            self.edited_block.size[0] = 0.0
                    elif self.text_input_action[3] == 'y_size':
                        if text:
                            self.edited_block.size[1] = float(text)
                        else:
                            self.edited_block.size[1] = 0.0
                elif self.text_input_action[2] == 'player':
                    if self.text_input_action[3] == 'x_pos':
                        if text:
                            self.edited_player_pos[0] = float(text)
                        else:
                            self.edited_player_pos[0] = 0.0
                    elif self.text_input_action[3] == 'y_pos':
                        if text:
                            self.edited_player_pos[1] = float(text)
                        else:
                            self.edited_player_pos[1] = 0.0
                elif self.text_input_action[2] == 'background':
                    if self.text_input_action[3] == 'color':
                        if text:
                            self.edited_background = int(text.ljust(6, '0'), 16)
                        else:
                            self.edited_background = 0xbbbbbb

    def load_player_data(self, file):
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
            else:
                for control in self.players[-1].controls:
                    if properky == control:
                        control_stuff = value.replace('[', '').replace(']', '').split(',')
                        if control_stuff[0] == '-1':
                            self.players[-1].controls[control] = [int(control_stuff[0]), int(control_stuff[1]), 0]
                        else:
                            if control_stuff[1].replace("'", '') == 'hat':
                                self.players[-1].controls[control] = [int(control_stuff[0]), control_stuff[1].replace("'", ''), int(control_stuff[2]), (int(control_stuff[3].replace('(', '')), int(control_stuff[4].replace(')', ''))), 0]
                            else:
                                self.players[-1].controls[control] = [int(control_stuff[0]), control_stuff[1].replace("'", ''), int(control_stuff[2]), int(control_stuff[3]), 0]
                        break

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
            file.write('    wins = ' + str(plajer.wins))
            for control in plajer.controls:
                file.write('\n    ' + control + ' = ' + str(plajer.controls[control][:-1]))
        file.close()



    def reset_editor_tools(self):
        self.tool = 'block'
        self.editor_block_color = 0x777777
        self.editor_block_solid = True
        self.editor_mirroring = False
        self.eraser_size = 60
        self.eraser_rect = [[0, 0], [0, 0]]
        self.mouse_step = 8
        self.soft_reset_editor_tools()

    def soft_reset_editor_tools(self):
        self.placing_block = False
        self.editor_block_pos = [0, 0]
        self.new_player_pos = [0, 0]
        self.edit_index = None
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
                              'page_entrance': 0,
                              'continual': 1}

    def get_editor_inputs(self):
        self.raw_mouse_input = pygame.mouse.get_pos()
        self.mouse_pos = [self.raw_mouse_input[0] / self.display_size[0] * self.levels[self.level].size[0], self.raw_mouse_input[1] / self.display_size[1] * self.levels[self.level].size[1]]
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

        for kontroller in self.controllers:
            kontroller.check_inputs(self.menu_controls, self.menu_input_delay_index, self.menu_controls['page_entrance'])

    def run_editor(self):
        lvl = self.levels[self.level]

        if self.menu_controls['up']:
            self.raw_mouse_input = [self.raw_mouse_input[0], self.raw_mouse_input[1] - self.mouse_step]# / self.display_size[1] * lvl.size[1]]
            if self.raw_mouse_input[1] < 0:
                self.raw_mouse_input[1] = 0
            pygame.mouse.set_pos(self.raw_mouse_input)
        if self.menu_controls['down']:
            self.raw_mouse_input = [self.raw_mouse_input[0], self.raw_mouse_input[1] + self.mouse_step]# / self.display_size[1] * lvl.size[1]]
            if self.raw_mouse_input[1] > self.display_size[1]:
                self.raw_mouse_input[1] = self.display_size[1] - 1
            pygame.mouse.set_pos(self.raw_mouse_input)
        if self.menu_controls['left']:
            self.raw_mouse_input = [self.raw_mouse_input[0] - self.mouse_step, self.raw_mouse_input[1]]# / self.display_size[0] * lvl.size[0], self.raw_mouse_input[1]]
            if self.raw_mouse_input[0] < 0:
                self.raw_mouse_input[0] = 0
            pygame.mouse.set_pos(self.raw_mouse_input)
        if self.menu_controls['right']:
            self.raw_mouse_input = [self.raw_mouse_input[0] + self.mouse_step, self.raw_mouse_input[1]]# / self.display_size[0] * lvl.size[0], self.raw_mouse_input[1]]
            if self.raw_mouse_input[0] > self.display_size[0]:
                self.raw_mouse_input[0] = self.display_size[0] - 1
            pygame.mouse.set_pos(self.raw_mouse_input)
        
        if self.menu_controls['back']:
            self.do_actions([['editor_display_level'], ['goto', 'editor_menu']])
        
        if (self.mouse_lmb and not self.mouse_last_lmb) or self.menu_controls['select']:
            if self.tool == 'block':
                if self.placing_block:
                    block = level_block()
                    block.color = self.editor_block_color
                    [block.pos, block.size] = point2size(self.editor_block_pos, self.mouse_pos)
                    block.solid = self.editor_block_solid
                    self.placing_block = False
                    if (block.size[0] > 0) and (block.size[1] > 0):
                        lvl.blocks.append(block)
                        if self.editor_mirroring:
                            blokk = level_block()
                            blokk.copy_from(block)
                            blokk.pos = [lvl.size[0] - block.pos[0] - block.size[0], block.pos[1]]
                            lvl.blocks.append(blokk)
                else:
                    self.editor_block_pos = self.mouse_pos
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
                for i in range(0, len(lvl.player_poses)):
                    h = len(lvl.player_poses) - i - 1
                    if in_rect(self.mouse_pos, lvl.player_poses[h], lvl.player_size):
                        edit_type = 'player'
                        self.edit_index = h
                        self.edited_player_pos = lvl.player_poses[h][:]
                        break
                if edit_type != 'player':
                    for i in range(0, len(lvl.blocks)):
                        h = len(lvl.blocks) - i - 1
                        if in_rect(self.mouse_pos, lvl.blocks[h].pos, lvl.blocks[h].size):
                            edit_type = 'block'
                            self.edit_index = h
                            self.edited_block = level_block()
                            self.edited_block.copy_from(lvl.blocks[self.edit_index])
                            break
                
                self.do_actions([['goto', 'edit_' + edit_type]])

        if self.tool == 'eraser':
            self.eraser_rect = [[self.mouse_pos[0] - self.eraser_size / 2, self.mouse_pos[1] - self.eraser_size / 2], [self.eraser_size, self.eraser_size]]
            if self.mouse_lmb or self.menu_controls['select']:
                player_poses_to_delete = []
                for i in range(0, len(lvl.player_poses)):
                    if rect_overlap(self.eraser_rect[0], self.eraser_rect[1], [0, 0], lvl.player_poses[i], lvl.player_size) != [0, 0]:
                        player_poses_to_delete.insert(0, i)
                for index in player_poses_to_delete:
                    lvl.player_poses.pop(index)
                blocks_to_delete = []
                for i in range(0, len(lvl.blocks)):
                    if rect_overlap(self.eraser_rect[0], self.eraser_rect[1], [0, 0], lvl.blocks[i].pos, lvl.blocks[i].size) != [0, 0]:
                        blocks_to_delete.insert(0, i)
                for index in blocks_to_delete:
                    lvl.blocks.pop(index)
        elif self.tool == 'player':
            self.new_player_pos = [self.mouse_pos[0] - lvl.player_size[0] / 2, self.mouse_pos[1] - lvl.player_size[1] / 2]
            while 1:
                no_overlap = True
                for block in lvl.blocks:
                    if block.solid:
                        overlap = rect_overlap(self.new_player_pos, lvl.player_size, [0, 0], block.pos, block.size, override = 1)
                        if overlap != [0, 0]:
                            no_overlap = False
                            self.new_player_pos = [self.new_player_pos[0], self.new_player_pos[1] + overlap[1]]
                            break
                if no_overlap:
                    for pos in lvl.player_poses:
                        overlap = rect_overlap(self.new_player_pos, lvl.player_size, [0, 0], pos, lvl.player_size, override = 1)
                        if overlap != [0, 0]:
                            no_overlap = False
                            self.new_player_pos = [self.new_player_pos[0], self.new_player_pos[1] + overlap[1]]
                            break
                    if no_overlap:
                        break
            
        if self.mouse_rmb and not self.mouse_last_rmb:
            if self.placing_block:
                self.placing_block = False
            else:
                found_player_pos = False
                for i in range(0, len(lvl.player_poses)):
                    h = len(lvl.player_poses) - i - 1
                    if in_rect(self.mouse_pos, lvl.player_poses[h], lvl.player_size):
                        lvl.player_poses.pop(h)
                        found_player_pos = True
                        break
                if not found_player_pos:
                    for i in range(0, len(lvl.blocks)):
                        h = len(lvl.blocks) - i - 1
                        if in_rect(self.mouse_pos, lvl.blocks[h].pos, lvl.blocks[h].size):
                            lvl.blocks.pop(h)
                            break
        
        self.editor_display_level(True)

    def editor_display_level(self, show_extra = False):
        lvl = self.levels[self.level]
        
        lvl.surface = pygame.Surface(lvl.size)
        lvl.surface.fill(lvl.background_color)

        for block in lvl.blocks:
            pygame.draw.rect(lvl.surface, block.color, [block.pos, block.size])

        for pos in lvl.player_poses:
            pygame.draw.rect(lvl.surface, 0xff0000, [pos, lvl.player_size])
            pygame.draw.rect(lvl.surface, 0xff8800, [[pos[0] + lvl.player_size[0] * 0.2, pos[1] + lvl.player_size[1] * 0.2], [lvl.player_size[0] * 0.6, lvl.player_size[1] * 0.6]])

        if show_extra:
            if self.tool == 'eraser':
                pygame.draw.rect(lvl.surface, 0xffbbbb, self.eraser_rect)
            elif self.tool == 'player':
                red_player = [self.new_player_pos, lvl.player_size]
                pygame.draw.rect(lvl.surface, 0xff0000, red_player)
                orange_player = [[self.new_player_pos[0] + lvl.player_size[0] * 0.2, self.new_player_pos[1] + lvl.player_size[1] * 0.2], [lvl.player_size[0] * 0.6, lvl.player_size[1] * 0.6]]
                pygame.draw.rect(lvl.surface, 0xff8800, orange_player)
            if self.placing_block:
                new_block = point2size(self.editor_block_pos, self.mouse_pos)
                pygame.draw.rect(lvl.surface, self.editor_block_color, new_block)
            if self.editor_mirroring:
                if self.tool == 'eraser':
                    pygame.draw.rect(lvl.surface, 0xffbbbb, reflect_rect(self.eraser_rect, lvl.size))
                elif self.tool == 'player':
                    pygame.draw.rect(lvl.surface, 0xff0000, reflect_rect(red_player, lvl.size))
                    pygame.draw.rect(lvl.surface, 0xff8800, reflect_rect(orange_player, lvl.size))
                if self.placing_block:
                    pygame.draw.rect(lvl.surface, self.editor_block_color, reflect_rect(new_block, lvl.size))
        pygame.transform.scale(lvl.surface, self.display_size, self.surface)



    def update(self):
        self.display.blit(pygame.transform.scale(self.surface, self.display_size), [0, 0])
        if self.show_fps:
            self.display.blit(text2img(str(0.1 * round(10 * self.clock.get_fps()))[0:4], 0, 'couriernew', 32, 1)[0], [16, 16])
        pygame.display.update()
        self.clock.tick(self.tick)
        self.page = self.next_page
    
    def close(self):
        pygame.quit()

class page():
    def __init__(self, file, display_size):
        self.blocks = []
        self.buttons = []
        self.controls = []
        self.lists = []
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
                [objekt.text_image, objekt.text_image_size] = text2img(objekt.text, objekt.text_color, objekt.text_font, objekt.text_size, objekt.text_bold)
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
                objekt.actions.append(value.split(':'))
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
    
    def append_objekt(self, objekt, objekt_type):
        if objekt_type == 'block':
            self.blocks.append(objekt)
        elif objekt_type == 'button':
            self.buttons.append(objekt)
        elif objekt_type == 'control':
            self.controls.append(objekt)
        elif objekt_type == 'list':
            self.lists.append(objekt)

class menu_block():
    def __init__(self):
        self.size = [0, 0]
        self.pos = [0, 0]
        self.color = -1
        self.dynamic_color = None
        self.alpha = 255
        self.text = ''
        self.text_variable = ''
        self.text_variable_char_limit = None
        self.text_color = 0x000000
        self.text_bold = 0
        self.text_font = 'couriernew'
        self.text_size = 1
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
        self.text_size = 1
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
        self.text = ''
        self.text_color = 0
        self.text_bold = 0
        self.text_font = 'couriernew'
        self.text_size = 1
        self.text_pos = [0, 0]
        self.text_limit = None
        self.wins_pos = [0, 0]
        self.kills_pos = [0, 0]
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

class controller():
    def __init__(self, joystick, joystick_threshold):
        self.joystick = joystick
        self.joystick_threshold = joystick_threshold
        self.flick_pause = 0.02
        self.flick_timestamp = [time.time() - self.flick_pause, time.time() - self.flick_pause]
        self.controls = {'up': [0, 0, -1, pygame.CONTROLLER_AXIS_LEFTY, pygame.CONTROLLER_BUTTON_DPAD_UP],
                         'down': [0, 0, 1, pygame.CONTROLLER_AXIS_LEFTY, pygame.CONTROLLER_BUTTON_DPAD_DOWN],
                         'left': [0, 0, -1, pygame.CONTROLLER_AXIS_LEFTX, pygame.CONTROLLER_BUTTON_DPAD_LEFT],
                         'right': [0, 0, 1, pygame.CONTROLLER_AXIS_LEFTX, pygame.CONTROLLER_BUTTON_DPAD_RIGHT],
                         'jump': [0, 0, -1, pygame.CONTROLLER_AXIS_LEFTY, pygame.CONTROLLER_BUTTON_A, pygame.CONTROLLER_BUTTON_B],
                         'shield': [0, 0, 2, pygame.CONTROLLER_AXIS_TRIGGERRIGHT, pygame.CONTROLLER_AXIS_TRIGGERLEFT, pygame.CONTROLLER_BUTTON_RIGHTSHOULDER, pygame.CONTROLLER_BUTTON_LEFTSHOULDER],
                         'select': [0, 0, 0, pygame.CONTROLLER_BUTTON_A, pygame.CONTROLLER_BUTTON_START],
                         'back': [0, 0, 0, pygame.CONTROLLER_BUTTON_B, pygame.CONTROLLER_BUTTON_BACK]}

    def check_inputs(self, menu_controls, menu_input_delay_index, is_first_frame):
        for control in self.controls:
            self.controls[control][1] = self.controls[control][0]
            self.controls[control][0] = 0
            for i in range(3, len(self.controls[control])):
                if abs(self.controls[control][2]) > i - 3:
                    if ((1 - 3 * (self.controls[control][2] < 0)) * self.joystick.get_axis(self.controls[control][i]) >= self.joystick_threshold):
                        self.controls[control][0] = 1
                        break
                elif self.joystick.get_button(self.controls[control][i]):
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

        for control in self.controls:
            if not is_first_frame:
                if self.controls[control][0] ^ self.controls[control][1]:
                    menu_controls[control] = self.controls[control][0]
                    if (control == 'up') or (control == 'down'):
                        menu_input_delay_index[1] = 0
                    elif (control == 'left') or (control == 'right'):
                        menu_input_delay_index[0] = 0

class player():
    def __init__(self, existing_players):
        self.name = 'Player ' + str(len(existing_players) + 1)
        self.base_color = 0xff0000
        self.color = 0
        self.alive = 0
        
        self.gravity = 0
        self.jump_strength = 0
        self.on_ground = 0

        self.pos = [0, 0]
        self.size = [0, 0]
        self.vel_terminal = [0, 0]
        self.vel_desired = [0, 0]
        self.vel_delta = [0, 0]
        self.vel = [0, 0]
        
        self.lpos = [0, 0]
        self.lvel = [0, 0]
        
        self.shield_health_base = 0
        self.shield_health = 0
        self.shield_regen = 0
        self.shield_broken = 0
        
        self.kills = 0
        self.wins = 0

        possible_controllers = len(existing_players) * 5 # <- Change this value to match number of controls a player has
        controller_number = possible_controllers + 1
        available_controllers = [0] * possible_controllers
        for plajer in existing_players:
            for control in plajer.controls:
                if plajer.controls[control][0] < possible_controllers:
                    available_controllers[plajer.controls[control][0]] = 1
        
        for i in range(0, len(available_controllers)):
            if available_controllers[i] == 0:
                controller_number = i
                break

        # Control: [controller # (0:), type, id, direction, value]
        # Control: [keyboard (-1), key, value]
        self.controls = {'left':    [controller_number, 'axis', 0, -1, 0],
                         'right':   [controller_number, 'axis', 0, 1, 0],
                         'jump':    [controller_number, 'button', 0, 1, 0],
                         'shield':  [controller_number, 'axis', 5, 1, 0],
                         'ability': [controller_number, 'button', 4, 1, 0]}
    
    def pos2(self):
        return [self.pos[0] + self.size[0], self.pos[1] + self.size[1]]

    def center(self):
        return [(self.pos[0] + self.size[0]) / 2, (self.pos[1] + self.size[1]) / 2]

    def soft_reset(self, pos, size, gravity, jump_strength, vel_terminal, vel_delta, player_shield_health_base, player_shield_regen):
        self.color = self.base_color
        self.alive = 1

        self.pos = pos
        self.vel = [0, 0]
        self.size = size
        self.gravity = gravity
        self.jump_strength = jump_strength
        self.vel_terminal = vel_terminal
        self.vel_delta = vel_delta
        
        self.shield_health_base = player_shield_health_base
        self.shield_health = self.shield_health_base
        self.shield_regen = player_shield_regen
        self.shield_broken = 0

        self.lpos = self.pos
        self.lvel = [0, 0]

        for control in self.controls:
            self.controls[control][-1] = 0

    def block_collision(self, block, lvl):
        k = self.vel[0] < self.vel[1]
        do_update_vel = 0
        for i in [k, not k]:
            if self.vel[i] and block.solid:
                if compare_wrapped(self.lpos, self.size, block.pos, block.size, lvl, not i):
                    if compare_wrapped(self.pos, self.size, block.pos, block.size, lvl, i):
                        if self.vel[i] >= 0:
                            result = find_wrapped_point(block.pos[i] - self.size[i], self.size, lvl, i)
                            self.pos[i] = result[0]
                        else:
                            result = find_wrapped_point(block.pos[i] + block.size[i], self.size, lvl, i)
                            self.pos[i] = result[0]
                        do_update_vel = 1
        if do_update_vel:
            self.update_vel(lvl)
        
    def player_collision(self, players, lvl, player_indeces):
        plajer = players[player_indeces[-1]]
        k = self.vel[0] < self.vel[1]
        do_update_vel = 0
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
                        do_update_vel = 1
        if do_update_vel:
            self.update_vel(lvl)

    def update_vel(self, lvl):
        # This assumes any movement larger that half the screen was a screen wrap
        self.vel = [self.pos[0] - self.lpos[0], self.pos[1] - self.lpos[1]]
        if lvl.horizontal_looping:
            if abs(self.vel[0]) > lvl.size[0] / 2:
                self.vel[0] = (self.vel[0] + lvl.size[0] / 2) % lvl.size[0] - lvl.size[0] / 2
        if lvl.vertical_looping:
            if abs(self.vel[1]) > lvl.size[1] / 2:
                self.vel[1] = (self.vel[1] + lvl.size[1] / 2) % lvl.size[1] - lvl.size[1] / 2

    def check_kill(self, lvl, players, kill_width, shield_color, player_index):
        for i in range(0, len(players)):
            if i != player_index:
                plajer = players[i]
                if plajer.alive and (plajer.color != shield_color):
                    if compare_wrapped([self.pos[0] + self.size[0] * (1 - kill_width) / 2, 0], [self.size[0] * kill_width, 0], [plajer.pos[0] + plajer.size[0] * (1 - kill_width) / 2, 0], [plajer.size[0] * kill_width, 0], lvl, 0, 1):
                        if compare_wrapped(self.pos, self.size, plajer.pos, [0, plajer.size[1] - self.size[1]], lvl, 1, 1):
                            plajer.alive = 0
                            self.kills += 1

    def check_ground(self, lvl, players, player_index):
        self.on_ground = 0
        for block in lvl.blocks:
            if block.solid:
                if compare_wrapped(self.pos, self.size, block.pos, block.size, lvl, 0, 1):
                    if compare_wrapped(self.pos, self.size, block.pos, [0, block.size[1] - self.size[1]], lvl, 1, 1):
                        self.on_ground = 1
                        return None
        for i in range(0, len(players)):
            if i != player_index:
                plajer = players[i]
                if plajer.alive:
                    if compare_wrapped(self.pos, self.size, plajer.pos, plajer.size, lvl, 0, 1):
                        if compare_wrapped(self.pos, self.size, plajer.pos, [0, plajer.size[1] - self.size[1]], lvl, 1, 1):
                            self.on_ground = 1
                            return None
        
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
                self.player_poses.append(findxy(value))
            elif properky == 'block':
                if objekt_type == 'block':
                    self.blocks.append(objekt)
                objekt_type = 'block'
                objekt = level_block()
            if objekt_type == 'level':
                if properky == 'size':
                    size = findxy(value)
                    self.size = [int(size[0]), int(size[1])]
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
                    objekt.size = findxy(value)
                elif properky == 'pos':
                    objekt.pos = findxy(value)
                elif properky == 'color':
                    objekt.color = int(value, 16)
                elif properky == 'solid':
                    objekt.solid = (value.lower() == 'true') or (value == '1')
        if objekt_type == 'block':
            self.blocks.append(objekt)

        self.surface = pygame.Surface(self.size)
        self.render_thumbnail()

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

    def render_thumbnail(self):
        self.thumbnail = pygame.Surface(self.size)
        self.thumbnail.fill(self.background_color)

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

def text2img(text, color, font, font_size, is_bold):
    font = pygame.font.SysFont(font, font_size, is_bold)
    rendered_text = font.render(text, False, color)
    text_size = font.size(text)
    return rendered_text, text_size

def in_rect(point, rect_pos, rect_size):
    for i in range(0, len(point)):
        if point[i] < rect_pos[i] or point[i] > rect_pos[i] + rect_size[i]:
            return 0
    return 1

def rect_overlap(p1, s1, v1, p2, s2, v2 = [0, 0], inclusive = 1, override = 0):
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

def compare_wrapped(p1, s1, p2, s2, lvl, i, inclusive = 0):
    if inclusive:
        if p1[i] + s1[i] >= p2[i]:
            if p2[i] + s2[i] >= p1[i]:
                return 1
        if p1[i] + s1[i] > lvl.size[i]:
            if ((i == 0) and lvl.horizontal_looping) or ((i == 1) and lvl.vertical_looping):
                if p1[i] + s1[i] - lvl.size[i] >= p2[i]:
                    if p2[i] + s2[i] >= p1[i] - lvl.size[i]:
                        return 1
    else:
        if p1[i] + s1[i] > p2[i]:
            if p2[i] + s2[i] > p1[i]:
                return 1
        if p1[i] + s1[i] > lvl.size[i]:
            if ((i == 0) and lvl.horizontal_looping) or ((i == 1) and lvl.vertical_looping):
                if p1[i] + s1[i] - lvl.size[i] > p2[i]:
                    if p2[i] + s2[i] > p1[i] - lvl.size[i]:
                        return 1
    return 0

def findxy(string, refrence_size = [0, 0], refrence_pos = [0, 0], self_size = [0, 0]):
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
    return xy

def findx(string, refrence_size = 0):
    # Find x 'word = xx'
    # 'x' means relative to refrence
    if string[0] == 'x':
        return refrence_size * float(string[1:])
    return float(string)

def point2size(p1, p2):
    p3 = [min(p1[0], p2[0]), min(p1[1], p2[1])]
    size = [abs(p1[0] - p2[0]), abs(p1[1] - p2[1])]
    return [p3, size]

def reflect_rect(rect, display_size):
    return [[display_size[0] - rect[0][0] - rect[1][0], rect[0][1]], rect[1]]