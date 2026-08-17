from src import cli


def test_tui_command_is_registered():
    command_functions = {command.callback.__name__ for command in cli.app.registered_commands}

    assert "launch_tui" in command_functions
