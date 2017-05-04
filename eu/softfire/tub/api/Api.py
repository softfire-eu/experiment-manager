import json
import os

import bottle
from beaker.middleware import SessionMiddleware
from bottle import request, post, get, HTTPError, HTTPResponse
from cork import Cork

from eu.softfire.tub.exceptions.exceptions import ManagerNotFound
from eu.softfire.tub.messaging.MessagingAgent import ManagerAgent
from eu.softfire.tub.utils.static_config import CONFIGURATION_FOLDER
from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger('eu.softfire.tub.api')

manager_agent = ManagerAgent()
aaa = Cork(get_config("api", "cork-files-path", "/etc/softfire/users"))
authorize = aaa.make_auth_decorator(fail_redirect="/login")


@get('/list_resources')
@authorize(role="experimenter")
def list_resources():
    try:
        return dict(
            resources=manager_agent.list_resources()
        )
    except ManagerNotFound as e:
        raise HTTPError(status=404, exception=e)


@get('/api/v1/resources/<id>')
@authorize(role="experimenter")
def list_resources(_id):
    try:
        return manager_agent.list_resources(_id=_id)
    except ManagerNotFound as e:
        raise HTTPError(status=404, exception=e)


@get('/api/v1/resources/<manager_name>')
@authorize(role="experimenter")
def list_resources(manager_name):
    try:
        return manager_agent.list_resources(manager_name)
    except ManagerNotFound as e:
        raise HTTPError(status=404, exception=e)


@post('/api/v1/resources')
def book_resources():
    logger.debug(("got body: %s" % request.body.read()))
    return HTTPResponse(status=201)


def start():
    bottle.debug(True)
    port = get_config(section='api', key='port', default=8080)
    app = bottle.app()
    session_opts = {
        'session.cookie_expires': True,
        'session.encrypt_key': 'softfire',
        'session.httponly': True,
        'session.timeout': 3600 * 24,  # 1 day
        'session.type': 'cookie',
        'session.validate_key': True,
    }
    app = SessionMiddleware(app, session_opts)
    bottle.run(app=app, quiet=False, reloader=True, port=port)


def postd():
    return bottle.request.forms


def post_get(name, default=''):
    try:
        return json.loads(request.body.read().decode("utf-8")).get(name, default)
    except:
        return bottle.request.POST.get(name, default).strip()


@bottle.post('/login')
def login():
    """Authenticate users"""
    username = post_get('username')
    password = post_get('password')
    aaa.login(username, password, success_redirect='/', fail_redirect='/login')


@bottle.route('/logout')
def logout():
    aaa.logout(success_redirect='/login')


def check_if_authorized(username):
    authorized_experimenter_file = get_config('api', 'authorized-experimenters',
                                              '/etc/softfire/authorized-experimenters.json')
    if os.path.exists(authorized_experimenter_file) and os.path.isfile(authorized_experimenter_file):
        with open(authorized_experimenter_file, "r") as f:
            authorized_exp = json.loads(f.read().encode("utf-8"))
            return authorized_exp.get(username) and bool(authorized_exp[username])
    else:
        return False


@bottle.post('/register')
def register():
    """Send out registration email"""
    logger.debug(("got body: %s" % request.body.read().decode("utf-8")))
    if check_if_authorized(post_get('username')):
        aaa.create_user(post_get('username'), 'user', post_get('password'))
    else:
        return HTTPError(status=401)
    return 'User created'


def add_authorized_experimenter(username):
    if not os.path.exists(CONFIGURATION_FOLDER):
        os.makedirs(CONFIGURATION_FOLDER)
    authorized_experimenter_file = get_config('api', 'authorized-experimenters',
                                              '/etc/softfire/authorized-experimenters.json')
    with open(authorized_experimenter_file, 'w') as f:
        authorized_exp = json.loads(f.read().encode("utf-8"))
        authorized_exp[username] = True
        f.write(json.dumps(authorized_exp))


@bottle.post('/add-authorized-experimenter')
def register():
    """Send out registration email"""
    logger.debug(("got body: %s" % request.body.read().decode("utf-8")))
    add_authorized_experimenter(post_get('username'))
    return 'User created'


@bottle.post('/reset_password')
def send_password_reset_email():
    """Send out password reset email"""
    aaa.send_password_reset_email(
        username=post_get('username'),
        email_addr=post_get('email_address')
    )
    return 'Please check your mailbox.'


@bottle.route('/change_password/:reset_code')
@bottle.view('password_change_form')
def change_password(reset_code):
    """Show password change form"""
    return dict(reset_code=reset_code)


@bottle.post('/change_password')
def change_password():
    """Change password"""
    aaa.reset_password(post_get('reset_code'), post_get('password'))
    return 'Thanks. <a href="/login">Go to login</a>'


@bottle.route('/')
@authorize()
def index():
    """Only authenticated users can see this"""
    # session = bottle.request.environ.get('beaker.session')
    # aaa.require(fail_redirect='/login')
    return 'Welcome! <br /> <a href="/admin">Admin page</a><br /> <a href="/logout">Logout</a> <br /> <a href="/experimenter">Experimenter</a>'


@bottle.route('/my_role')
def show_current_user_role():
    """Show current user role"""
    session = bottle.request.environ.get('beaker.session')
    logger.debug("Session from simple_webapp", repr(session))
    aaa.require(fail_redirect='/login')
    return aaa.current_user.role


# Admin-only pages

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


@bottle.post('/create_user')
def create_user():
    try:
        aaa.create_user(postd().username, postd().role, postd().password)
        return dict(ok=True, msg='')
    except Exception as e:
        return dict(ok=False, msg=e.message)


@bottle.post('/delete_user')
def delete_user():
    try:
        aaa.delete_user(post_get('username'))
        return dict(ok=True, msg='')
    except Exception as e:
        logger.debug(repr(e))
        return dict(ok=False, msg=e.message)


@bottle.post('/create_role')
def create_role():
    try:
        aaa.create_role(post_get('role'), post_get('level'))
        return dict(ok=True, msg='')
    except Exception as e:
        return dict(ok=False, msg=e.message)


@bottle.post('/delete_role')
def delete_role():
    try:
        aaa.delete_role(post_get('role'))
        return dict(ok=True, msg='')
    except Exception as e:
        return dict(ok=False, msg=e.message)


# Static pages

@bottle.route('/login')
@bottle.view('login_form')
def login_form():
    """Serve login form"""
    return {}


@bottle.route('/experimenter')
@bottle.view('experimenter')
def login_form():
    """Serve experimenter form"""
    return dict(
        current_user=aaa.current_user,
        users=aaa.list_users(),
        roles=aaa.list_roles(),
        resources=[manager_agent.list_resources()]
    )


@bottle.route('/sorry_page')
def sorry_page():
    """Serve sorry page"""
    return '<p>Sorry, you are not authorized to perform this action</p>'


@bottle.route('/static/<filename>')
def server_static(filename):
    if ".." in filename:
        return HTTPError(status=403)
    return bottle.static_file(filename, root='%s/../../../../static' % os.path.dirname(os.path.realpath(__file__)))
