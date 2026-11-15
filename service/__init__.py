"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import sys
from flask import Flask
from flask_talisman import Talisman
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from service import config
from service.common import log_handlers

# Create Flask application
app = Flask(__name__)
app.config.from_object(config)

# Trust X-Forwarded-Proto/Host from one proxy hop (the OpenShift router),
# so the app knows when the original client request was HTTPS.
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Security: add standard security headers (X-Frame-Options, CSP, etc.).
# HTTP->HTTPS redirect is opt-in via FORCE_HTTPS because TLS is terminated
# at the router/ingress and the pod itself only serves plain HTTP on 8080.
talisman = Talisman(app, force_https=config.FORCE_HTTPS)

# Security: allow cross-origin requests from other microservices
CORS(app)

# Import the routes After the Flask app is created
# pylint: disable=wrong-import-position, cyclic-import, wrong-import-order
from service import routes, models  # noqa: F401 E402

# pylint: disable=wrong-import-position
from service.common import error_handlers, cli_commands  # noqa: F401 E402

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    models.init_db(app)  # make our database tables
except Exception as error:  # pylint: disable=broad-except
    app.logger.critical("%s: Cannot continue", error)
    # gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

app.logger.info("Service initialized!")
