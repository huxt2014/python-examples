

"""
                 +--------+
                 | Server |
                 +--------+
                      |
            environ + start_response

    +-----------------|-------------------------------------------------------+
    | Flask           |                                                       |
    |                                                                         |
    |    +-------- bind context ----+                                         |
    |    |                          |                  +----------+           |
    |    |   bind request instance  |    +--------->   |    rv    |           |
    |    |            |             |    |             +----------+           |
    |    |   bind session instance  |    |                   |                |
    |    |            |             |    |      +--------finalize---------+   |
    |    +------------|-------------+    |      |            |            |   |
    |                                    |      |      make_response      |   |
    |      before_first_request_funcs    |      |            |            |   |
    |                 |                  |      | after_request_functions |   |
    |    +------ pre-process -------+    |      |            |            |   |
    |    |                          |    |      |       save session      |   |
    |    | url_value_preprocessors  |    |      |            |            |   |
    |    |            |             |    |      +------------|------------+   |
    |    |  before_request_funcs    |    |                                    |
    |    |            |             |    |      +----- unbind context ----+   |
    |    +------------|-------------+    |      |                         |   |
    |                                    |      |    do_teardown_request  |   |
    |    +--------dispatch----------+    |      |            |            |   |
    |    |            |             |    |      |      close request      |   |
    |    |     view_functions       |    |      |            |            |   |
    |    |            |             -----+      +------------|------------+   |
    |    |     handle exception     |                                         |
    |    |        if raised         |                  +----------+           |
    |    +--------------------------+                  | Response |           |
    |                                                  +----------+           |
    +--------------------------------------------------------|----------------+



                                         +---------------------------+
                                         |Server                     |
                                         |                           |
                                         |    +-----------------+    |
    +--------+         +-------+         |    |Middleware       |    |
    |        | ----->  |       | ----->  |    |                 |    |
    | Client |         | Proxy |         |    |    +-------+    |    |
    |        | <-----  |       | <-----  |    |    | Flask |    |    |
    +--------+         +-------+         |    |    +-------+    |    |
                                         |    +-----------------+    |
                                         |                           |
                                         +---------------------------+
"""
