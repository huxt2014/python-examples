
from flask import Flask, url_for, request, jsonify, abort, make_response


app = Flask(__name__)


###############################################################################
#                                 route
#     By default, a route only answers to GET requests. Besides, HEAD and
# OPTIONS are added automatically.
###############################################################################
@app.route('/')
def index():
    return 'index page'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return 'POST'
    else:
        return 'GET'


@app.route('/user/<username>')
def show_user_profile(username):
    return "user %s" % username


# valid converters:
# string, int, float, path, any, uuid
@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'post %s' % post_id


# generate url through function name
assert url_for(index) == '/'
assert url_for(show_post, post_id=1, p1=1) == 'post/1?p1=1'


###############################################################################
#                                 response
###############################################################################

def example1():
    data = 1
    if data == 1:
        abort(400)
    elif data == 2:
        return make_response('message', 200)
    else:
        return jsonify(key1=1, key2=2)


###############################################################################
#                                  request
###############################################################################

# form ##########################################################
# if the key does not exist in the form attribute, KeyError is
# raised. If you don't cache that, a HTTP 400 Bad Request error
# page is shown instead.
username = request.form['username']
password = request.form['password']

# data ##########################################################
# If the mimetype is application/json this will contain the
# parsed JSON data. Otherwise this will be None.
request.get_json(force=True,              # ignore mimetype
                 silent=True)             # fail silently and return None
