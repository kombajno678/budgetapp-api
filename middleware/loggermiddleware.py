class LoggerMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        #print('Log middleware')
        return self.app(environ, start_response)
