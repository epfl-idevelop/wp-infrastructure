import os
import socket
ADMINS = ()

AWX_PROOT_ENABLED = False

# Automatically deprovision pods that go offline
AWX_AUTO_DEPROVISION_INSTANCES = True

SYSTEM_TASK_ABS_CPU = 6
SYSTEM_TASK_ABS_MEM = 20

INSIGHTS_URL_BASE = "https://example.org"

#Autoprovisioning should replace this
CLUSTER_HOST_ID = socket.gethostname()
SYSTEM_UUID = '00000000-0000-0000-0000-000000000000'

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

REMOTE_HOST_HEADERS = ['HTTP_X_FORWARDED_FOR']

STATIC_ROOT = '/var/lib/awx/public/static'
PROJECTS_ROOT = '/var/lib/awx/projects'
JOBOUTPUT_ROOT = '/var/lib/awx/job_status'
SECRET_KEY = open('/etc/tower/conf.d/django_secret_key', 'rb').read().strip()
ALLOWED_HOSTS = ['*']
INTERNAL_API_URL = 'http://127.0.0.1:8052'
SERVER_EMAIL = 'root@localhost'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'
EMAIL_SUBJECT_PREFIX = '[AWX] '
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

# Maximum ?page_size= value in API queries
MAX_PAGE_SIZE = 1000

LOGGING['handlers']['console'] = {
    '()': 'logging.StreamHandler',
    'level': 'DEBUG',
    'formatter': 'simple',
}

LOGGING['loggers']['django.request']['handlers'] = ['console']
LOGGING['loggers']['rest_framework.request']['handlers'] = ['console']
LOGGING['loggers']['awx']['handlers'] = ['console']
LOGGING['loggers']['awx.main.commands.run_callback_receiver']['handlers'] = ['console']
LOGGING['loggers']['awx.main.commands.inventory_import']['handlers'] = ['console']
LOGGING['loggers']['awx.main.tasks']['handlers'] = ['console']
LOGGING['loggers']['awx.main.scheduler']['handlers'] = ['console']
LOGGING['loggers']['django_auth_ldap']['handlers'] = ['console']
LOGGING['loggers']['social']['handlers'] = ['console']
LOGGING['loggers']['system_tracking_migrations']['handlers'] = ['console']
LOGGING['loggers']['rbac_migrations']['handlers'] = ['console']
LOGGING['loggers']['awx.isolated.manager.playbooks']['handlers'] = ['console']
LOGGING['handlers']['callback_receiver'] = {'class': 'logging.NullHandler'}
LOGGING['handlers']['fact_receiver'] = {'class': 'logging.NullHandler'}
LOGGING['handlers']['task_system'] = {'class': 'logging.NullHandler'}
LOGGING['handlers']['tower_warnings'] = {'class': 'logging.NullHandler'}
LOGGING['handlers']['rbac_migrations'] = {'class': 'logging.NullHandler'}
LOGGING['handlers']['system_tracking_migrations'] = {'class': 'logging.NullHandler'}
LOGGING['handlers']['management_playbooks'] = {'class': 'logging.NullHandler'}

USE_X_FORWARDED_PORT = True
