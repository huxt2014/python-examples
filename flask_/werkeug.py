

from werkzeug.wrappers import Response, Request

###############################################################################
#                            Response
#     The Response is a standard WSGI application. It's initialized with a
# couple of response parameters (headers, body, status code etc.) and will start
# a valid WSGI response when called with the environ and start response
# callable.
#     The response object is mutable. It can be pickled or copied after freeze()
# was called. It's possible to create copies using copy.deepcopy.
#     Since Werkzeug 0.6 it's safe to use the same response object for multiple
# WSGI responses.
###############################################################################

# construct #######################################################
# For most mime types mimetype and content_type work the same, but
# the charset. If the mimetype passed and starting with text/, the
# charset is set. In contrast the content_type parameter is always
#  added as header unmodified.
response = Response('Hello World', status=200)

# inspect #########################################################
# headers
response.headers['Content-Encoding'] = 'gzip'

# request body
response.get_data()
response.set_data()

# cookies
response.set_cookie('username', 'John')

# get (app_iter, status, headers)
response.get_wsig_response()


###############################################################################
#                            Request
#     The request object is immutable. Modifications are not supported by
# default, you may however replace the immutable attributes with mutable
# attributes if you need to modify it.
#     The request object may be shared in the same thread, but is not thread
# safe itself.
#     It's not possible to pickle the request object.
###############################################################################
environ = {'REQUEST_METHOD': 'GET',
           'PATH_INFO': '/',
           'SERVER_PROTOCOL': 'HTTP/1.1',
           'QUERY_STRING': ''}

request = Request(environ)

# path
assert request.path == '/'

# method
assert request.method == 'POST'

# headers
request.headers.get('Accept-Encoding', '')

# form
username = request.form['username']
password = request.form['password']

# parameters
key = request.args.get('key', '')

# cookies
username2 = request.cookies.get('username')
