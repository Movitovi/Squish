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
        game.play_snake()
    elif game.mode == 'scythe':
        game.play_scythe()
    game.update()
game.close()