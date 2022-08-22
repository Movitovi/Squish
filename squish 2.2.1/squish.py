import func
game = func.game()
while game.running:
    if game.mode == 'page':
        game.get_page_inputs()
        game.run_page()
    elif game.mode == 'in_game':
        game.get_level_inputs()
        game.run_level()
    elif game.mode == 'editor':
        game.get_editor_inputs()
        game.run_editor()
    game.update()
game.close()