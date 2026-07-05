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
    from engine.cli.volume import volume_cmd
    from engine.cli.feeling import feeling_cmd
    from engine.cli.action import action_cmd
    from engine.cli.dial import dial_cmd
    from engine.cli.qualia import qualia_cmd
    from engine.cli.bubble import bubble_cmd
    from engine.cli.interest import interest_cmd
    from engine.cli.recall import recall_cmd
    from engine.cli.memory import memory_app
    app.command("setup", help="Interactive setup wizard")(setup)
    app.command("start", help="Start TTS server + avatar")(start)
    app.command("stop", help="Stop the running server")(stop)
    app.command("status", help="Check server status")(status)
    app.command("download", help="Download language packs")(download)
    app.command("speak", help="Speak text via avatar")(speak_cmd)
    app.command("volume", help="Show or set standing speech volume (0-100)")(volume_cmd)
    app.command("feeling", help="Set avatar feeling")(feeling_cmd)
    app.command("action", help="Trigger avatar action")(action_cmd)
    app.command("dial", help="Show or set Saori's feel dials")(dial_cmd)
    app.command("qualia", help="Unified inner-state write: dials + qualia pushes + revalue")(qualia_cmd)
    app.command("bubble", help="Enter/switch/leave the active bubble; bare = status")(bubble_cmd)
    app.command("interest", help="Raise an interest lens (pack print); bare = the shelf")(interest_cmd)
    app.command("recall", help="Search the memory index: ranked gists + pointers")(recall_cmd)
    app.add_typer(memory_app, name="memory")


_register_commands()

if __name__ == "__main__":
    app()
