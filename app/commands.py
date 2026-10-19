import click
from flask.cli import with_appcontext
from .seed import seed_demo_data

def register_commands(app):
    @app.cli.command("seed-demo")
    @with_appcontext
    def seed_command():
        """Carga datos de demostración (borra primero datos operativos existentes)."""
        counts = seed_demo_data()
        click.echo(f"Seed terminado: {counts}")
