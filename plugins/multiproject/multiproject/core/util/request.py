# -*- coding: utf-8 -*-
"""
Module for requesting custom, multiproject based data from a request. This offers utilities
to ensure that the request has the dict for holding certain data commonly needed to be
fetched several times in a single request.

Other alternatives to provide this kind of functionality would be to implement something
with memoization pattern, where functions would remember the data based on their own
parameters.

This module is not meant to duplicate the api in core modules, but some duplication
most likely cannot be avoided, as the data fetched, and how it's fetched, is identical
to database queries.
"""


def get_context(req):
    """
    Gets context out of the request. Creates one into the request if none is found.

    This is meant to help Trac Components to store data into temporary context for
    requests, especially if the same data is needed in several components during the
    same request.

    Example of use:

    .. code-block:: python

        from multiproject.core.util.request import get_context

        def process_request(self, req):
            the_data = None
            context = get_context(req)

            if 'mykey' in context:
                # ... get the data
                the_data = context['mykey']
            else:
                # .. get the data from elsewhere
                the_data = TheData()
                context['mykey'] = the_data

            # ... And do the thing

    :param Request req: The Trac request to get the context from
    :returns: The dict containing multiproject specific data for the request
    """
    if not hasattr(req, "multiproject"):
        setattr(req, "multiproject", {})

    return req.multiproject

def get_user(req, userkey):
    """
    Gets user from request by user_id or by username, depending on which was given
    in as an argument. If no user is found, None is returned.

    Example of use in a Trac Component:

    .. code-block:: python

        from multiproject.core.util.request import get_user, store_user

        class MyComponent(Component):
            def process_request(self, req):
                user = get_user(req, req.authname)
                if user is None:
                    store = MySqlUserStore()
                    user = store.getUser(req.authname)

                    if user is None:
                        raise TracError('Invalid user')

                    store_user(req, user)

                # Do the thing with user

    Now, no doubt the use looks like it's only adding code complexity. Which it does. But
    this will overall increase performance, when the amount of memcache and mysql queries
    go down.

    :param Request req: The Trac request to check for the user data
    :param userkey: Either the userid in database or username of the user
    :returns: User object if it is found
    """
    if userkey is None:
        raise ValueError('User key must contain a valid username')

    ctx = get_context(req)

    return ctx.get("user:{0}".format(userkey), None)

def store_user(req, user):
    """
    Stores user object into the context. The user object is stored twice, into the dict,
    with userid and username. Both are used as accessors and are mandatory for user object.

    For example of use see :func:`multiproject.core.utils.request.get_user`

    :param Request req: The Trac request object
    :param User user: The Multiproject user object, as fetched from database or memcache
    """
    if user is None:
        raise ValueError('User object must contain a valid user')

    ctx = get_context(req)

    ctx["user:{0}".format(user.id)] = user
    ctx["user:{0}".format(user.username)] = user
