"""Log utilities."""
# -----------------------------------------------------------------------------
#  Copyright (c) Jupyter Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
# -----------------------------------------------------------------------------
import json

from tornado.log import access_log

from .auth import User
from .prometheus.log_functions import prometheus_log_method


def log_request(handler):
    """log a bit more information about each request than tornado's default

    - move static file get success to debug-level (reduces noise)
    - get proxied IP instead of proxy IP
    - log referer for redirect and failed requests
    - log user-agent for failed requests
    """
    status = handler.get_status()
    request = handler.request
    try:
        logger = handler.log
    except AttributeError:
        logger = access_log

    if status < 300 or status == 304:  # noqa[PLR2004]
        # Successes (or 304 FOUND) are debug-level
        log_method = logger.debug
    elif status < 400:  # noqa[PLR2004]
        log_method = logger.info
    elif status < 500:  # noqa[PLR2004]
        log_method = logger.warning
    else:
        log_method = logger.error

    request_time = 1000.0 * handler.request.request_time()
    ns = {
        "status": status,
        "method": request.method,
        "ip": request.remote_ip,
        "uri": request.uri,
        "request_time": request_time,
    }
    # log username
    # make sure we don't break anything
    # in case mixins cause current_user to not be a User somehow
    try:
        user = handler.current_user
    except Exception:
        user = None
    username = (user.username if isinstance(user, User) else "unknown") if user else ""
    ns["username"] = username

    msg = "{status} {method} {uri} ({username}@{ip}) {request_time:.2f}ms"
    if status >= 400:  # noqa[PLR2004]
        # log bad referers
        ns["referer"] = request.headers.get("Referer", "None")
        msg = msg + " referer={referer}"
    if status >= 500 and status != 502:  # noqa[PLR2004]
        # Log a subset of the headers if it caused an error.
        headers = {}
        for header in ["Host", "Accept", "Referer", "User-Agent"]:
            if header in request.headers:
                headers[header] = request.headers[header]
        log_method(json.dumps(headers, indent=2))
    log_method(msg.format(**ns))
    prometheus_log_method(handler)
