from authlib.integrations.flask_client import OAuth
from flask import Flask, request, jsonify, url_for, render_template, redirect
import flask_praetorian
from flask_cors import CORS
from forms import AdminLoginForm
from model import init_db, User
from views import blueprint as api


def create_app(config_file='config.py'):
    guard = flask_praetorian.Praetorian()
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    app_cors_config = {
        "origins": ["*"],
        "methods": ["OPTIONS", "GET", "POST", "PATCH", "PUT"],
        "allow_headers": ["Authorization", "Content-type"]
    }
    CORS(app, resources={"/*": app_cors_config})

    # oauth init
    oauth = OAuth(app)
    oauth.register(
        name='github',
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )

    # praetorian init
    guard.init_app(app, User)

    # SQLAlchemy init
    init_db(app, guard, 'tests' in config_file)

    # register blueprint
    app.register_blueprint(api, url_prefix="/api/")

    # admin authentication login
    @app.route('/', methods=['GET', 'POST'])
    def admin():
        """
            Process login requests

            Get login credentials from form_data
            Parameters: username and password
        """
        form = AdminLoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = guard.authenticate(username, password)
            user_roles = [role.name for role in user.roles]

            if user is not None and "admin" in user_roles:
                return redirect(url_for("Winning Horse.doc"))
            form.username.errors.append("Error: Introduce ADMIN credentials to login")

        return render_template("admin_login.html", form=form)

    # client authentication login
    @app.route('/login', methods=['POST'])
    def login():
        """
        Process login requests

        Get login credentials from body using json
        Parameters: username and password
        """
        username = request.json.get('username')
        password = request.json.get('password')

        user = guard.authenticate(username, password)
        ret = {"access_token": guard.encode_jwt_token(user)}

        return jsonify(ret), 200

    @app.route('/github')
    def oauth_login():
        """
        Send gitHub authorization request

        Creates Authlib client for OAuth with gitHub
        """

        github = oauth.create_client('github')
        redirect_uri = url_for('authorize', _external=True)
        return github.authorize_redirect(redirect_uri)

    @app.route('/authorize')
    def authorize():
        """
        Process gitHub authorization

        Redirect Uri for gitHub OAuth authorization
        """

        token = oauth.github.authorize_access_token()
        resp = oauth.github.get('user', token=token)
        resp.raise_for_status()
        profile = resp.json()

        user = User.lookup(profile.get("login"))
        ret = {"access_token": guard.encode_jwt_token(user)}

        # return JWT
        return jsonify(ret), 200

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
