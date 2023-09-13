""" boots up pystro app """
from flask import render_template, make_response, current_app
from flask_migrate import Migrate, upgrade
from flask_cors import CORS
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from api import create_app
from api.database import db
from api import init_api_data
from api.models.user import User
from api.models.restaurant import Restaurant
from api.models.menu import Item
from dashboard.admin_models import OrderAdmin, ItemModelView, SectionModelView, RestaurantModelView
import os
from flask import jsonify

import logging

app = create_app(debug=True)
CORS(app)


app.static_folder = '/home/mint/Websites/test/smartlunch-client'
app.template_folder = '../smartlunch-client/src'
app.static_url_path = ''


# Initialize Flask-Admin
dashboard = Admin(app, name='Pystro-Admin',
                  template_mode='bootstrap4', url='/dashboard', endpoint='dashboard')
dashboard.add_view(ModelView(User, db.session))
dashboard.add_view(RestaurantModelView(Restaurant, db.session))
dashboard.add_view(ItemModelView(Item, db.session))


@app.route('/show-routes')
def show_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule))
    logging.debug(routes)
    # Retrieve environment variables
    env_vars = dict(os.environ)

    # Filter out only the relevant env vars or mask secrets if necessary
    relevant_keys = ['FLASK_APP', 'FLASK_ENV',
                     'SECRET_KEY', 'DATABASE_URL', 'PORT']
    env_vars = {k: env_vars[k] if k not in [
        'SECRET_KEY', 'DATABASE_URL'] else '****' for k in relevant_keys if k in env_vars}

    return render_template('routes.html', routes=routes, env_vars=env_vars)


@app.route('/debug/path')
def debug_path():
    return jsonify({
        "current_working_directory": os.getcwd(),
        "app_template_folder": app.template_folder,
        "app_static_folder": app.static_folder,
        "__file__": __file__
    })


@app.route('/')
def index():
    return render_template('index.html')


@app.shell_context_processor
def make_shell_context():
    """ initializes vars for flask shell """
    return dict(app=app, db=db, User=User, Restaurant=Restaurant)


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()
    # creates initial data
    init_api_data(app)
