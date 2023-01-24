import sqlite3

import click
from flask import current_app, g
# g unique for each request, used to store data that might be acessed by multiple functions during request.
# connection is stord and reused rather than creating a new connection.


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],  # current_app object that points to the Flask application handling request.
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # tells the connection to return rows that behave like dicts.

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)  # tells Flask to call the function when cleaning up after returning the response.
    app.cli.add_command(init_db_command)  # adds a new command that can be called with the flask command.

