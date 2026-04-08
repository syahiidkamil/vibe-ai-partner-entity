"""Vibe AI Partner CLI — entry point."""

import typer

app = typer.Typer(
    name="vibe",
    help="Vibe AI Partner — TTS + Avatar CLI",
    no_args_is_help=True,
)


def _register_commands() -> None:
    from vibe.cli.setup import setup
    from vibe.cli.start import start
    from vibe.cli.stop import stop
    from vibe.cli.status import status
    from vibe.cli.download import download
    from vibe.cli.speak import speak_cmd
    from vibe.cli.feeling import feeling_cmd
    from vibe.cli.action import action_cmd

    app.command("setup", help="Interactive setup wizard")(setup)
    app.command("start", help="Start TTS server + avatar")(start)
    app.command("stop", help="Stop the running server")(stop)
    app.command("status", help="Check server status")(status)
    app.command("download", help="Download language packs")(download)
    app.command("speak", help="Speak text via TTS")(speak_cmd)
    app.command("feeling", help="Set avatar feeling")(feeling_cmd)
    app.command("action", help="Trigger avatar action")(action_cmd)


_register_commands()

if __name__ == "__main__":
    app()
