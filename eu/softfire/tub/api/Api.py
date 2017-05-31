import json
import logging
import os
import traceback

import bottle
from beaker.middleware import SessionMiddleware
from bottle import request, post, get, HTTPError
from cork import Cork

import eu.softfire.tub.exceptions.exceptions as exceptions
from eu.softfire.tub.core import CoreManagers
from eu.softfire.tub.core.CoreManagers import get_resources_dict, get_images, CalendarManager, Experiment, \
    get_experiment_dict, create_user_info
from eu.softfire.tub.utils.static_config import CONFIGURATION_FOLDER
from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger('eu.softfire.tub.api')
bottle.TEMPLATE_PATH = [get_config('api', 'view-path', '/etc/softfire/views')]
aaa = Cork(get_config("api", "cork-files-path", "/etc/softfire/users"))
authorize = aaa.make_auth_decorator(fail_redirect="/login")


######################
# Experimenters urls #
######################

@post('/provide_resources')
@authorize(role='experimenter')
def provide_resources():
    CoreManagers.provide_resources(aaa.current_user.username)
    bottle.redirect('/experimenter')


@post('/release_resources')
@authorize(role='experimenter')
def delete_resources():
    CoreManagers.release_resources(aaa.current_user.username)
    bottle.redirect('/experimenter')


@get('/refresh_images')
@authorize(role='experimenter')
def refresh_resources():
    CoreManagers.refresh_resources(aaa.current_user.username)


@get('/get_status')
@authorize(role='experimenter')
def get_status():
    experiment_dict = CoreManagers.get_experiment_dict(aaa.current_user.username)
    bottle.response.headers['Content-Type'] = 'application/json'
    return json.dumps(experiment_dict)


@post('/reserve_resources')
@authorize(role='experimenter')
def book_resources():
    data = request.files.get('data')
    logger.debug("files: %s" % list(request.files.keys()))
    for file in request.files:
        logger.debug("file %s" % file)
    logger.debug("Data: '%s'" % data)
    # logger.debug("Data.file: %s" % data.file)
    if data and data.file:
        Experiment(data.file, username=aaa.current_user.username).reserve()
        bottle.redirect('/experimenter')
    logger.debug(("got body: %s" % request.body.read()))
    raise FileNotFoundError("File not found in your request")


#################
# General pages #
#################

@bottle.post('/login')
def login():
    """Authenticate users"""
    username = post_get('username')
    password = post_get('password')
    if not aaa.login(username, password):
        return dict(ok=False, msg="Username or password invalid")
    if aaa.current_user.role == 'admin':
        return dict(
            ok=True,
            redirect="/admin"
        )
    else:
        return dict(
            ok=True,
            redirect="/experimenter"
        )


@bottle.route('/logout')
def logout():
    aaa.logout(success_redirect='/login')


@bottle.post('/register')
def register():
    """Send out registration email"""
    logger.debug(("got body: %s" % request.body.read().decode("utf-8")))
    if check_if_authorized(post_get('username')):
        aaa.create_user(post_get('username'), 'user', post_get('password'))
    else:
        return dict(
            ok=False,
            msg="username not pre authorized"
        )
    return 'User created'


# @bottle.post('/reset_password')
# def send_password_reset_email():
#     """Send out password reset email"""
#     aaa.send_password_reset_email(
#         username=post_get('username'),
#         email_addr=post_get('email_address')
#     )
#     return 'Please check your mailbox.'


# @bottle.post('/change_password')
# def change_password():
#     """Change password"""
#     aaa.reset_password(post_get('reset_code'), post_get('password'))
#     return 'Thanks. <a href="/login">Go to login</a>'


@bottle.route('/')
@authorize()
def index():
    """Only authenticated users can see this"""
    return 'Welcome! <br /> ' \
           '<a href="/admin">Admin page</a> <br /> ' \
           '<a href="/experimenter">Experimenter</a> <br /> ' \
           '<a href="/logout">Logout</a> <br /> '


@bottle.route('/my_role')
def show_current_user_role():
    """Show current user role"""
    session = bottle.request.environ.get('beaker.session')
    logger.debug("Session from simple_webapp", repr(session))
    aaa.require(fail_redirect='/login')
    return aaa.current_user.role


###############
# Admin pages #
###############

@bottle.post('/add-authorized-experimenter')
@authorize(role='admin')
def register():
    """Send out registration email"""
    logger.debug(("got body: %s" % request.body.read().decode("utf-8")))
    add_authorized_experimenter(post_get('username'))
    return 'User created'


@bottle.post('/create_user')
@authorize(role='admin')
def create_user():
    try:
        password = postd().password
        role = postd().role
        username = postd().username
        create_user_info(username=username, password=password, role=role)
        aaa.create_user(username, role, password)
        return dict(ok=True, msg='Create user %s' % username)
    except Exception as e:
        traceback.print_exc()
        if not hasattr(e, 'message'):
            return dict(ok=False, msg=e.args)
        return dict(ok=False, msg=e.message)


@bottle.post('/delete_user')
@authorize(role='admin')
def delete_user():
    try:
        aaa.delete_user(post_get('username'))
        return dict(ok=True, msg='')
    except Exception as e:
        logger.debug(repr(e))
        return dict(ok=False, msg=e.args)


@bottle.post('/create_role')
@authorize(role='admin')
def create_role():
    try:
        aaa.create_role(post_get('role'), post_get('level'))
        return dict(ok=True, msg='')
    except Exception as e:
        return dict(ok=False, msg=e.args)


@bottle.post('/delete_role')
@authorize(role='admin')
def delete_role():
    try:
        aaa.delete_role(post_get('role'))
        return dict(ok=True, msg='')
    except Exception as e:
        return dict(ok=False, msg=e.args)


################
# Static pages #
################


@bottle.route('/admin')
@authorize(role="admin", fail_redirect='/sorry_page')
@bottle.view('admin_page')
def admin():
    """Only admin users can see this"""
    # aaa.require(role='admin', fail_redirect='/sorry_page')
    return dict(
        current_user=aaa.current_user,
        users=aaa.list_users(),
        roles=aaa.list_roles()
    )


@bottle.route('/login')
@bottle.view('login_form')
def login_form():
    """Serve login form"""
    return {}


@bottle.route('/experimenter')
@bottle.view('experimenter')
@authorize(role="experimenter", fail_redirect='/sorry_page')
def login_form():
    """Serve experimenter form"""
    return dict(
        current_user=aaa.current_user,
        resources=get_resources_dict(),
        images=get_images(),
        experiment_id="",
        experiment_resources=get_experiment_dict(aaa.current_user.username),
    )


# @bottle.route('/change_password/:reset_code')
# @bottle.view('password_change_form')
# def change_password(reset_code):
#     """Show password change form"""
#     return dict(reset_code=reset_code)


@bottle.route('/calendar')
@bottle.view('calendar')
@authorize(role="experimenter", fail_redirect='/sorry_page')
def get_calendar():
    return dict(
        calendar=CalendarManager.get_month(),
        current_user=aaa.current_user
    )


@bottle.route('/sorry_page')
def sorry_page():
    """Serve sorry page"""
    return '<p>Sorry, you are not authorized to perform this action</p>'


@bottle.route('/static/<filename>')
# @authorize(role="experimenter", fail_redirect='/sorry_page')
def server_static(filename):
    """ route to the css and static files"""
    if ".." in filename:
        return HTTPError(status=403)
    return bottle.static_file(filename, root='%s/../../../../static' % os.path.dirname(os.path.realpath(__file__)))


#########
# Utils #
#########

def error_translation(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            traceback.print_exc()
            bottle.abort(400, e.args)
        except exceptions.ExperimentNotFound as e:
            traceback.print_exc()
            bottle.abort(404, e.message)
        except exceptions.ExperimentValidationError as e:
            traceback.print_exc()
            bottle.abort(400, e.message)
        except exceptions.ManagerNotFound as e:
            traceback.print_exc()
            bottle.abort(404, e.message)
        except exceptions.ResourceAlreadyBooked as e:
            traceback.print_exc()
            bottle.abort(400, e.message)
        except exceptions.ResourceNotFound as e:
            traceback.print_exc()
            bottle.abort(404, e.message)
        except exceptions.RpcFailedCall:
            traceback.print_exc()
            bottle.abort(500, "Ups, an internal error occurred, please report to us the procedure and we will fix it")
        except FileNotFoundError:
            traceback.print_exc()
            bottle.abort(404, "File not found in your request")
        # except:
        #     traceback.print_exc()
        #     bottle.abort(500, "Ups, an internal error occurred, please report to us the procedure and we will fix it")

    return wrapper


def postd():
    return bottle.request.forms


def post_get(name, default=''):
    try:
        return json.loads(request.body.read().decode("utf-8")).get(name, default)
    except:
        return bottle.request.POST.get(name, default).strip()


def check_if_authorized(username):
    authorized_experimenter_file = get_config('api', 'authorized-experimenters',
                                              '/etc/softfire/authorized-experimenters.json')
    if os.path.exists(authorized_experimenter_file) and os.path.isfile(authorized_experimenter_file):
        with open(authorized_experimenter_file, "r") as f:
            authorized_exp = json.loads(f.read().encode("utf-8"))
            return authorized_exp.get(username) and bool(authorized_exp[username])
    else:
        return False


def add_authorized_experimenter(username):
    if not os.path.exists(CONFIGURATION_FOLDER):
        os.makedirs(CONFIGURATION_FOLDER)
    authorized_experimenter_file = get_config('api', 'authorized-experimenters',
                                              '/etc/softfire/authorized-experimenters.json')
    with open(authorized_experimenter_file, 'w') as f:
        authorized_exp = json.loads(f.read().encode("utf-8"))
        authorized_exp[username] = True
        f.write(json.dumps(authorized_exp))


def start():
    bottle.debug(True)
    port = get_config(section='api', key='port', default=8080)
    app = bottle.app()
    bottle.install(error_translation)
    session_opts = {
        'session.cookie_expires': True,
        'session.encrypt_key': get_config('api', 'encrypt_key', 'softfire'),
        'session.httponly': True,
        'session.timeout': 3600 * 24,  # 1 day
        'session.type': 'cookie',
        'session.validate_key': True,
    }
    app = SessionMiddleware(app, session_opts)
    quiet_bottle = logger.getEffectiveLevel() < logging.DEBUG
    logger.debug("Bootlepy quiet mode: %s" % quiet_bottle)
    bottle.run(app=app, quiet=quiet_bottle, port=port, host='0.0.0.0')
