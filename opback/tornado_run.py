# -*- coding:utf-8 -*-
#
# Author: Shawn.Tai
# Email: shawntai.ds@gmail.com
#

from promise import app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import tornado.options

app.config.update(DEBUG=True)

from tornado.options import define, options
define("port", default=5000, help="run on the given port", type=int)

# http_server = HTTPServer(WSGIContainer(app))
# http_server.listen(options.port)
# IOLoop.instance().start()
if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(options.port)
    IOLoop.instance().start()
