import json
import os
import traceback
from multiprocessing.dummy import Pool

import bottle
import requests
from beaker.middleware import SessionMiddleware
from bottle import request, post, get, HTTPError, HTTPResponse, hook
from cork import Cork

import eu.softfire.tub.exceptions.exceptions as exceptions
from eu.softfire.tub.core import CoreManagers
from eu.softfire.tub.core.CoreManagers import get_resources_dict, Experiment, \
    get_experiment_dict, add_resource, get_other_resources
from eu.softfire.tub.core.calendar import CalendarManager
from eu.softfire.tub.core.certificate import CertificateGenerator, log_certificate_create
from eu.softfire.tub.utils.static_config import CONFIGURATION_FOLDER
from eu.softfire.tub.utils.utils import get_config, get_logger

logger = get_logger('eu.softfire.tub.api')
bottle.TEMPLATE_PATH = [get_config('api', 'view-path', '/etc/softfire/views')]
aaa = Cork(get_config("api", "cork-files-path", "/etc/softfire/users"))
authorize = aaa.make_auth_decorator(fail_redirect="/login")
create_user_thread = None
create_user_thread_pool = Pool(20)


@hook('after_request')
def maintenance():
    try:
        if request.environ.get('bottle.raw_path') == '/login' or aaa.current_user.role == 'admin':
            return
    except:
        return
    if CoreManagers.maintenance:
        raise HTTPResponse("Under maintenance. Please try again in a few minutes.")

######################
# Experimenters urls #
######################

@post('/provide_resources')
@authorize(role='experimenter')
def provide_resources():
    experiment_id = post_get('experiment_id')
    CoreManagers.provide_resources(aaa.current_user.username, experiment_id)
    bottle.redirect('/experimenter')


@post('/release_resources')
@authorize(role='experimenter')
def delete_resources():
    experiment_id = post_get('experiment_id')
    CoreManagers.release_resources(aaa.current_user.username, experiment_id)
    bottle.redirect('/experimenter')


@get('/refresh_images')
@authorize(role='experimenter')
def refresh_resources():
    CoreManagers.refresh_resources(aaa.current_user.username)
    CoreManagers.list_resources()


@get('/get_full_status')
@authorize(role='experimenter')
def get_full_status():
    _, _, experiment_dict = CoreManagers.get_experiment_dict(aaa.current_user.username)
    # convert string values that represent json into dictionaries so that they are displayed nicely
    for e in experiment_dict:
        try:
            parsed_value = json.loads(e.get('value'))
            e['value'] = parsed_value
        except:
            pass
    bottle.response.headers['Content-Type'] = 'application/json'
    return json.dumps(experiment_dict, indent=4, sort_keys=True)


@get('/get_status')
@authorize(role='experimenter')
def get_status():
    _, _, experiment_dict = CoreManagers.get_experiment_dict(aaa.current_user.username)
    experiment_dict = __format_experiment_dict(experiment_dict)
    bottle.response.headers['Content-Type'] = 'application/json'
    return json.dumps(experiment_dict)


@post('/check_user')
@authorize(role='portal')
def get_status():
    username = post_get('username')
    user = aaa.user(username)
    bottle.response.headers['Content-Type'] = 'application/json'
    if user:
        return HTTPResponse(body=json.dumps(dict(msg="User %s exists" % username, ok=True)), status=200)
    else:
        return HTTPResponse(body="User %s does not exists" % username, status=404)


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


@post('/add_resource')
@authorize(role='experimenter')
def create_resource():
    resource_id = request.forms.get('id')
    node_type = request.forms.get('node_type')
    cardinality = request.forms.get('cardinality')
    description = request.forms.get('description')
    testbed = request.forms.get('testbed')
    upload = request.files.get('upload')
    add_resource(aaa.current_user.username, resource_id, node_type, cardinality, description, testbed, upload)
    bottle.redirect('/experimenter')


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


@bottle.post('/certificates')
# @authorize(role='admin')
@authorize(role='portal')
def get_certificate():
    username = post_get('username')
    if not username:
        raise bottle.HTTPError(500, "Username missing")
    password = post_get('password', default=None)
    days = int(post_get('days', default=None))
    cert_gen = CertificateGenerator()
    log_certificate_create(username, days)
    cert_gen.generate(password, username, days)
    openvpn_config = cert_gen.get_openvpn_config()
    headers = {
        'Content-Type': 'text/plain;charset=UTF-8',
        'Content-Disposition': 'attachment; filename="softfire-vpn_%s.ovpn"' % username,
        "Content-Length": len(openvpn_config)
    }
    return bottle.HTTPResponse(openvpn_config, 200, **headers)


@bottle.post('/create_user')
@authorize(role='portal')
def create_user():
    password = postd().password
    role = postd().role
    username = postd().username
    create_user_thread_pool.apply_async(create_user_thread_function, args=(username, password, role,))
    return HTTPResponse("Creating user %s in progress" % username, status=202)


@bottle.post('/refresh_user')
@authorize(role='admin')
def refresh_user():
    global create_user_thread
    username = postd().username
    CoreManagers.refresh_user(username)
    return HTTPResponse("Refreshed user %s." % username, status=200)


@bottle.post('/delete_user')
@authorize(role='portal')
def delete_user():
    username = post_get('username')
    try:
        CoreManagers.delete_user(username)
        aaa.delete_user(username)
        return dict(ok=True, msg='Deleted {}'.format(username))
    except Exception as e:
        error_message = 'Deletion of user {} failed: {}'.format(username, str(e))
        logger.error(error_message)
        traceback.print_exc()
        bottle.response.status = 400
        return dict(ok=False, msg=error_message)


@bottle.post('/create_role')
@authorize(role='admin')
def create_role():
    aaa.create_role(post_get('role'), int(post_get('level')))
    return dict(ok=True, msg='')


@bottle.post('/delete_role')
@authorize(role='admin')
def delete_role():
    aaa.delete_role(post_get('role'))
    return dict(ok=True, msg='')


@get('/get_resources')
@authorize(role='admin')
def get_status():
    resources = CoreManagers.get_all_resources()
    bottle.response.headers['Content-Type'] = 'application/json'
    return json.dumps(resources)


@get('/experimenters')
@authorize(role='admin')
def get_status():
    bottle.response.headers['Content-Type'] = 'application/json'
    return json.dumps(CoreManagers.list_experimenters())

@bottle.post('/enable_maintenance')
@authorize(role='admin')
def enable_maintenance():
    """Enable maintenance mode so that experimenters cannot execute actions anymore."""
    CoreManagers.maintenance = True
    bottle.response.status = 200
    return dict(ok=False, msg='Maintenance enabled')

@bottle.post('/disable_maintenance')
@authorize(role='admin')
def disable_maintenance():
    """Disable maintenance mode."""
    CoreManagers.maintenance = False
    bottle.response.status = 200
    return dict(ok=False, msg='Maintenance disabled')


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
        roles=aaa.list_roles(),
        managers=CoreManagers.list_managers(),
        experimenters=CoreManagers.list_experimenters(),
    )


@bottle.route('/login')
@bottle.view('login_form')
def login_form():
    """Serve login form"""
    return {}


@bottle.route('/experimenter')
@bottle.view('experimenter')
@authorize(role="experimenter", fail_redirect='/sorry_page')
def experimenter_form():
    """Serve experimenter form"""
    images, networks, flavours = get_other_resources()
    exp_names, exp_ids, experiment_dict = get_experiment_dict(aaa.current_user.username)
    experiment_dict = __format_experiment_dict(experiment_dict)
    return dict(
        current_user=aaa.current_user,
        resources=get_resources_dict(),
        user_resources=get_resources_dict(aaa.current_user.username),
        images=images,
        networks=networks,
        flavours=flavours,
        experiment_resources=experiment_dict,
        ids=exp_ids,
    )


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


@bottle.route('/static/<filename:path>')
# @authorize(role="experimenter", fail_redirect='/sorry_page')
def server_static(filename):
    """ route to the css and static files"""
    if ".." in filename:
        return HTTPError(status=403)
    return bottle.static_file(filename, root='%s/static' % get_config('api', 'view-path', '/etc/softfire/views'))


#########
# Utils #
#########

@bottle.route('/heartbeat')
def sorry_page():
    return 'OK'


def error_translation(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            pass
            traceback.print_exc()
            return HTTPResponse(status=400, body=e.args)
            # bottle.abort(400, e.args)
        except exceptions.ExperimentNotFound as e:
            traceback.print_exc()
            return HTTPResponse(status=404, body=e.message)
            # bottle.abort(404, e.message)
        except exceptions.ExperimentValidationError as e:
            traceback.print_exc()
            return HTTPResponse(status=400, body=e.message)
            # bottle.abort(400, e.message)
        except exceptions.ManagerNotFound as e:
            traceback.print_exc()
            return HTTPResponse(status=404, body=e.message)
            # bottle.abort(404, e.message)
        except exceptions.ResourceAlreadyBooked as e:
            traceback.print_exc()
            return HTTPResponse(status=400, body=e.message)
            # bottle.abort(400, e.message)
        except exceptions.ResourceNotFound as e:
            traceback.print_exc()
            return HTTPResponse(status=404, body=e.message)
            # bottle.abort(404, e.message)
        except exceptions.RpcFailedCall:
            traceback.print_exc()
            return HTTPResponse(status=500,
                                body="Ups, an internal error occurred, please report to us the procedure and we will fix it")
            # bottle.abort(500, "Ups, an internal error occurred, please report to us the procedure and we will fix it")
        except FileNotFoundError as e:
            traceback.print_exc()
            return HTTPResponse(status=404, body=e.args)
            # bottle.abort(404, "File not found in your request")

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


def __format_experiment_dict(experiment):
    """
    Format the experiment value. In case an NSR is in the experiment value, only it's most important fields are
    kept, so that the user is not confused by the amount of information.
    :param experiment:
    :return:
    """
    formatted_experiment = []
    for resource in experiment:
        if resource.get('node_type') == 'NfvResource' and resource.get('status') == 'DEPLOYED':
            full_nsr = resource.get('value')
            try:
                full_nsr = json.loads(full_nsr)
            except:
                logger.warning('Could not parse NSR of resource: {}'.format(resource.get('resource_id')))
                formatted_experiment.append(resource)
                continue

            formatted_nsr = {}

            for key in ['name', 'version', 'status']:
                value = full_nsr.get(key)
                if value is not None:
                    formatted_nsr[key] = value

            vnfr_list = full_nsr.get('vnfr')
            if vnfr_list is not None and isinstance(vnfr_list, list):
                formatted_vnfr_list = []
                for vnfr in vnfr_list:
                    formatted_vnfr = {}
                    for key in ['name', 'type', 'status']:
                        value = vnfr.get(key)
                        if value is not None:
                            formatted_vnfr[key] = value

                    # add error description if lifecycle events failed
                    vnfr_status = vnfr.get('status')
                    if vnfr_status is not None and vnfr_status == 'ERROR':
                        for lifecycle_event in vnfr.get('lifecycle_event_history'):
                            if lifecycle_event.get('event') == 'ERROR':
                                if formatted_vnfr.get('failed lifecycle events') is None:
                                    formatted_vnfr['failed lifecycle events'] = []
                                formatted_vnfr.get('failed lifecycle events').append(
                                    '{}: {}'.format(lifecycle_event.get('executedAt'),
                                                    lifecycle_event.get('description')))

                    private_ip_list = []
                    floating_ip_list = []
                    vdu_list = vnfr.get('vdu')
                    if vdu_list is not None and isinstance(vdu_list, list):
                        for vdu in vdu_list:
                            vnfc_instance_list = vdu.get('vnfc_instance')
                            if vnfc_instance_list is not None and isinstance(vnfc_instance_list, list):
                                for vnfc_instance in vnfc_instance_list:
                                    if vnfc_instance.get('floatingIps') is not None and isinstance(
                                            vnfc_instance.get('floatingIps'), list):
                                        vnfc_floating_ip_list = ['{}:{}'.format(fip.get('netName'), fip.get('ip')) for
                                                                 fip in vnfc_instance.get('floatingIps')]
                                        floating_ip_list.extend(vnfc_floating_ip_list)
                                    if vnfc_instance.get('ips') is not None and isinstance(vnfc_instance.get('ips'),
                                                                                           list):
                                        vnfc_private_ip_list = ['{}:{}'.format(fip.get('netName'), fip.get('ip')) for
                                                                fip in vnfc_instance.get('ips')]
                                        private_ip_list.extend(vnfc_private_ip_list)
                    formatted_vnfr['private IPs'] = private_ip_list
                    formatted_vnfr['floating IPs'] = floating_ip_list
                    formatted_vnfr_list.append(formatted_vnfr)
                formatted_nsr['vnfr'] = formatted_vnfr_list

            resource['value'] = json.dumps(formatted_nsr)
        formatted_experiment.append(resource)
    return formatted_experiment


def setup_app() -> (SessionMiddleware, int, bool):
    bottle.debug(True)
    p = get_config(section='api', key='port', default=5080)
    bottle.install(error_translation)
    session_opts = {
        'session.cookie_expires': True,
        'session.encrypt_key': get_config('api', 'encrypt_key', 'softfire'),
        'session.httponly': True,
        'session.timeout': 3600 * 24,  # 1 day
        'session.type': 'cookie',
        'session.validate_key': True,
    }
    a = SessionMiddleware(bottle.app(), session_opts)
    qb = get_config('api', 'quiet', 'true').lower() == 'true'
    logger.debug("Bootlepy quiet mode: %s" % qb)
    return a, p, qb


app, port, quiet_bottle = setup_app()


def start_listening():
    logger.info("Running bottle app: quiet=%s, port=%s, host='0.0.0.0'" % (quiet_bottle, port))
    bottle.run(app, server='paste', host='0.0.0.0', port=port, quiet=quiet_bottle)


def create_user_thread_function(username, password, role='experimenter'):
    """
    This function is expected to be executed in a thread pool and called by the Api's create_user function.
    :param username: 
    :param password: 
    :param role: 
    :return: 
    """
    try:
        CoreManagers.create_user(username=username, password=password, role=role)
        res = requests.post("http://localhost:%s/create_user_local" % port,
                            json=dict(username=username, password=password, role=role))
        if res.status_code != 200:
            logger.error('Not able to create cork user {}, return status {}: {}'.format(username, res.status_code,
                                                                                        str(res.content)))
            try:
                logger.debug('Try to delete user {} for rollback after creation in cork failed'.format(username))
                CoreManagers.delete_user(username=username)
            except Exception as e:
                logger.error(
                    'Deletion of user {} for rollback after cork user creation failed did not succeed: {}'.format(
                        username, e))

    except Exception as e:
        error_message = 'Create user \'{}\' failed: {}'.format(username, str(e))
        logger.error(error_message)
        traceback.print_exc()


@post("/create_user_local")
def _create_user_cork():
    logger.debug("Remote addr: %s" % request.remote_addr)
    if "localhost" in request.remote_addr or "127.0.0.1" in request.remote_addr:
        try:
            aaa.login(username='admin', password=get_config('system', 'admin-password', 'softfire'))
            aaa.create_user(request.json.get('username'), request.json.get('role'), request.json.get('password'))
        except Exception as e:
            return HTTPResponse(status=400, body=str(e))
        return HTTPResponse(status=200)
    else:
        return HTTPResponse(status=404)
