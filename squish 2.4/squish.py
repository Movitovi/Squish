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
    elif game.mode == 'snake':
        game.get_snake_inputs()
        game.play_snake()
    elif game.mode == 'scythe':
        game.get_scythe_inputs()
        game.play_scythe()
    elif game.mode == 'tron':
        game.get_level_inputs()
        game.play_tron()
    game.update()
game.close()