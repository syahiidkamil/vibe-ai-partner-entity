"""VAPE — Vibe AI Partner Entity CLI."""

import typer

app = typer.Typer(
    name="vape",
    help="VAPE — Vibe AI Partner Entity",
    no_args_is_help=True,
)


def _register_commands() -> None:
    from vape.cli.setup import setup
    from vape.cli.start import start
    from vape.cli.stop import stop
    from vape.cli.status import status
    from vape.cli.download import download
    from vape.cli.speak import speak_cmd
    from vape.cli.feeling import feeling_cmd
    from vape.cli.action import action_cmd
    app.command("setup", help="Interactive setup wizard")(setup)
    app.command("start", help="Start TTS server + avatar")(start)
    app.command("stop", help="Stop the running server")(stop)
    app.command("status", help="Check server status")(status)
    app.command("download", help="Download language packs")(download)
    app.command("speak", help="Speak text via avatar")(speak_cmd)
    app.command("feeling", help="Set avatar feeling")(feeling_cmd)
    app.command("action", help="Trigger avatar action")(action_cmd)


_register_commands()

if __name__ == "__main__":
    app()
