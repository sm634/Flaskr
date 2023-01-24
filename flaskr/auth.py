import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))  # assiciates the URL/register with the register view function. When
# flask receives a request to /auth/register, it will call the register view and ust eh return value as the response.
def register():
    if request.method == 'POST':
        username = request.form['username']  # request.form a special type of dict mapping submitted. The user will
        # input their username and password.
        password = request.form['password']
        db = get_db()
        error = None

        # validate that username and password are not empty.
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # insert new user into database.
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),  # securely hash the password.
                )
                db.commit()  # commit changes
            except db.IntegrityError:  # raised if user already exists.
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            session.clear()  # session is a dict that stores data across requests. When validation succeeds, the user's
            # id is stored in a new session. The data is stored in a cookie that is sent to the browser, and the
            # browser then sends it back with subsequent requests.
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request  # registers a function that runs before the view function, no matter what URL is requested.
def load_logged_in_user():
    """Checks if a user id is stored in the session and gets the user's data from the database, storing it on g.user,
    which lasts for the length of the request. If there is no user id, or if the id doesn't exist,
    g.user will be None."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)  # decorator to check if the user creating, editing or deleting is logged in.
    def wrapped_view(**kwargs):
        """function checks if a user is loaded and redirects to the login page otherwise"""
        if g.user is None:
            return redirect(url_for('auth.login'))  # url_for() function generates the URL to a view based on a name
        # and arguments. The name associated with a view is also called the endpoint, and by default it's the same
        # as the name of the view function.

        return view(**kwargs)

    return wrapped_view

