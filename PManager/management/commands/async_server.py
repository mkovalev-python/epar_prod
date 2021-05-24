# -*- coding: utf-8 -*-
__author__ = 'Gvammer'
from tornado import web, gen, ioloop, httpserver
from server import MyConnection
from django.core.management.base import NoArgsCommand
from optparse import Option
import os

ROOT = os.path.normpath(os.path.dirname(__file__))
make_option = Option


class Command(NoArgsCommand):
    option_list = (
        make_option('-p', '--port', action='store', dest='port', default='8082',
                    help='Port for server binding'),
        make_option('-f', '--fport', action='store', dest='fport', default='843',
                    help='Port for flashpolicy'),
        make_option('--settings',
                    help='The Python path to a settings module, e.g. "myproject.settings.main". If this isn\'t provided, the DJANGO_SETTINGS_MODULE environment variable will be used.'),
        make_option('--pythonpath',
                    help='A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".'),
        make_option('--traceback', action='store_true',
                    help='Print traceback on exception'),
        make_option('-v', '--verbosity', action='store', dest='verbosity', default='1',
                    type='choice', choices=['0', '1', '2', '3'],
                    help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output'),
    )
    # def handle(self, *args, **options):
    # if args[0]:
    #         port = args[0]
    #     else:
    #         port = 8001
    #
    #     # Create TornadIO2 router
    #     router = TornadioRouter(MyConnection)
    #
    #     # Create Tornado application with urls from router
    #     app = web.Application(
    #         router.urls,
    #         socket_io_port=port,
    #         socket_io_address=settings.SOCKET_SERVER_ADDRESS,
    #         flash_policy_port = 843,
    #         flash_policy_file = os.path.join(ROOT, 'flashpolicy.xml'),
    #     )
    #
    #     SocketServer(app)


    def handle_noargs(self, **options):

        if 'port' in options:
            port = options['port']
        else:
            port = 8082

        if 'fport' in options:
            fport = int(options['fport'])
        else:
            fport = 843


        def make_app():
            return web.Application([
                (r'/', MyConnection),
            ])

        app = make_app()
        app.listen(port)
        ioloop.IOLoop.current().start()
