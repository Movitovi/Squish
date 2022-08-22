import func
game = func.game()
while game.running:
    game.get_inputs()
    if game.page == 'menu':
        # Select Level
        # Level Editor
        # Players/Controls
        # Quit
        game.handle_menu()
        game.display_menu()
        pass
    elif game.page == 'level select':
        # Level list w/ preview
        # Press back to return to Menu
        game.handle_level_select()
        game.display_level_select()
    elif game.page == 'level':
        # Load level
        # Play game
        # Once one left win the game
        game.handle_level()
        game.display_level()
    elif game.page == 'level win':
        # Show winner for a while
        # Then return to the main menu
        game.handle_win()
        game.display_win()
    elif game.page == 'level edit select':
        # Select level
        # Copy existing level
        # New level
        # Press back to return to Menu
        game.handle_level_edit_select()
        game.display_level_edit_select()
    elif game.page == 'level editor properties':
        # Select name
        # Select size
        # Select if player properties are global
        # Select background color
        # Select vertical looping (Add color if deadly boundary)
        # Select horizontal looping (Add wall if not looping)
        game.handle_level_editor_properties()
        game.display_level_editor_properties()
    elif game.page == 'level editor':
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
        game.handle_level_editor()
        game.display_level_editor()
    elif game.page == 'settings':
        # Update joysticks
        # Map player
        game.handle_settings()
        game.display_settings()
    game.update()
game.close()