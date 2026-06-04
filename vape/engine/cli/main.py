"""VAPE — Vibe AI Partner Entity CLI."""

import typer

app = typer.Typer(
    name="vape",
    help="VAPE — Vibe AI Partner Entity",
    no_args_is_help=True,
)


def _register_commands() -> None:
    from engine.cli.setup import setup
    from engine.cli.start import start
    from engine.cli.stop import stop
    from engine.cli.status import status
    from engine.cli.download import download
    from engine.cli.speak import speak_cmd
    from engine.cli.feeling import feeling_cmd
    from engine.cli.action import action_cmd
    from engine.cli.dial import dial_cmd
    from engine.cli.qualia import qualia_cmd
    app.command("setup", help="Interactive setup wizard")(setup)
    app.command("start", help="Start TTS server + avatar")(start)
    app.command("stop", help="Stop the running server")(stop)
    app.command("status", help="Check server status")(status)
    app.command("download", help="Download language packs")(download)
    app.command("speak", help="Speak text via avatar")(speak_cmd)
    app.command("feeling", help="Set avatar feeling")(feeling_cmd)
    app.command("action", help="Trigger avatar action")(action_cmd)
    app.command("dial", help="Show or set Saori's feel dials")(dial_cmd)
    app.command("qualia", help="Unified inner-state write: dials + qualia pushes + revalue")(qualia_cmd)


_register_commands()

if __name__ == "__main__":
    app()
