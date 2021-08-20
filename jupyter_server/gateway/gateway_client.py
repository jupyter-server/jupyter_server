# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json
import os
from socket import gaierror

from tornado import web
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPError
from traitlets import Bool
from traitlets import default
from traitlets import Float
from traitlets import Int
from traitlets import TraitError
from traitlets import Unicode
from traitlets import validate
from traitlets.config import SingletonConfigurable


class GatewayClient(SingletonConfigurable):
    """This class manages the configuration.  It's its own singleton class so that we
    can share these values across all objects.  It also contains some helper methods
     to build request arguments out of the various config options.

    """

    url = Unicode(
        default_value=None,
        allow_none=True,
        config=True,
        help="""The url of the Kernel or Enterprise Gateway server where
        kernel specifications are defined and kernel management takes place.
        If defined, this Notebook server acts as a proxy for all kernel
        management and kernel specification retrieval.  (JUPYTER_GATEWAY_URL env var)
        """,
    )

    url_env = "JUPYTER_GATEWAY_URL"

    @default("url")
    def _url_default(self):
        return os.environ.get(self.url_env)

    @validate("url")
    def _url_validate(self, proposal):
        value = proposal["value"]
        # Ensure value, if present, starts with 'http'
        if value is not None and len(value) > 0:
            if not str(value).lower().startswith("http"):
                raise TraitError("GatewayClient url must start with 'http': '%r'" % value)
        return value

    ws_url = Unicode(
        default_value=None,
        allow_none=True,
        config=True,
        help="""The websocket url of the Kernel or Enterprise Gateway server.  If not provided, this value
        will correspond to the value of the Gateway url with 'ws' in place of 'http'.  (JUPYTER_GATEWAY_WS_URL env var)
        """,
    )

    ws_url_env = "JUPYTER_GATEWAY_WS_URL"

    @default("ws_url")
    def _ws_url_default(self):
        default_value = os.environ.get(self.ws_url_env)
        if default_value is None:
            if self.gateway_enabled:
                default_value = self.url.lower().replace("http", "ws")
        return default_value

    @validate("ws_url")
    def _ws_url_validate(self, proposal):
        value = proposal["value"]
        # Ensure value, if present, starts with 'ws'
        if value is not None and len(value) > 0:
            if not str(value).lower().startswith("ws"):
                raise TraitError("GatewayClient ws_url must start with 'ws': '%r'" % value)
        return value

    kernels_endpoint_default_value = "/api/kernels"
    kernels_endpoint_env = "JUPYTER_GATEWAY_KERNELS_ENDPOINT"
    kernels_endpoint = Unicode(
        default_value=kernels_endpoint_default_value,
        config=True,
        help="""The gateway API endpoint for accessing kernel resources (JUPYTER_GATEWAY_KERNELS_ENDPOINT env var)""",
    )

    @default("kernels_endpoint")
    def _kernels_endpoint_default(self):
        return os.environ.get(self.kernels_endpoint_env, self.kernels_endpoint_default_value)

    kernelspecs_endpoint_default_value = "/api/kernelspecs"
    kernelspecs_endpoint_env = "JUPYTER_GATEWAY_KERNELSPECS_ENDPOINT"
    kernelspecs_endpoint = Unicode(
        default_value=kernelspecs_endpoint_default_value,
        config=True,
        help="""The gateway API endpoint for accessing kernelspecs (JUPYTER_GATEWAY_KERNELSPECS_ENDPOINT env var)""",
    )

    @default("kernelspecs_endpoint")
    def _kernelspecs_endpoint_default(self):
        return os.environ.get(
            self.kernelspecs_endpoint_env, self.kernelspecs_endpoint_default_value
        )

    kernelspecs_resource_endpoint_default_value = "/kernelspecs"
    kernelspecs_resource_endpoint_env = "JUPYTER_GATEWAY_KERNELSPECS_RESOURCE_ENDPOINT"
    kernelspecs_resource_endpoint = Unicode(
        default_value=kernelspecs_resource_endpoint_default_value,
        config=True,
        help="""The gateway endpoint for accessing kernelspecs resources
            (JUPYTER_GATEWAY_KERNELSPECS_RESOURCE_ENDPOINT env var)""",
    )

    @default("kernelspecs_resource_endpoint")
    def _kernelspecs_resource_endpoint_default(self):
        return os.environ.get(
            self.kernelspecs_resource_endpoint_env, self.kernelspecs_resource_endpoint_default_value
        )

    connect_timeout_default_value = 40.0
    connect_timeout_env = "JUPYTER_GATEWAY_CONNECT_TIMEOUT"
    connect_timeout = Float(
        default_value=connect_timeout_default_value,
        config=True,
        help="""The time allowed for HTTP connection establishment with the Gateway server.
        (JUPYTER_GATEWAY_CONNECT_TIMEOUT env var)""",
    )

    @default("connect_timeout")
    def connect_timeout_default(self):
        return float(
            os.environ.get("JUPYTER_GATEWAY_CONNECT_TIMEOUT", self.connect_timeout_default_value)
        )

    request_timeout_default_value = 40.0
    request_timeout_env = "JUPYTER_GATEWAY_REQUEST_TIMEOUT"
    request_timeout = Float(
        default_value=request_timeout_default_value,
        config=True,
        help="""The time allowed for HTTP request completion. (JUPYTER_GATEWAY_REQUEST_TIMEOUT env var)""",
    )

    @default("request_timeout")
    def request_timeout_default(self):
        return float(
            os.environ.get("JUPYTER_GATEWAY_REQUEST_TIMEOUT", self.request_timeout_default_value)
        )

    client_key = Unicode(
        default_value=None,
        allow_none=True,
        config=True,
        help="""The filename for client SSL key, if any.  (JUPYTER_GATEWAY_CLIENT_KEY env var)
        """,
    )
    client_key_env = "JUPYTER_GATEWAY_CLIENT_KEY"

    @default("client_key")
    def _client_key_default(self):
        return os.environ.get(self.client_key_env)

    client_cert = Unicode(
        default_value=None,
        allow_none=True,
        config=True,
        help="""The filename for client SSL certificate, if any.  (JUPYTER_GATEWAY_CLIENT_CERT env var)
        """,
    )
    client_cert_env = "JUPYTER_GATEWAY_CLIENT_CERT"

    @default("client_cert")
    def _client_cert_default(self):
        return os.environ.get(self.client_cert_env)

    ca_certs = Unicode(
        default_value=None,
        allow_none=True,
        config=True,
        help="""The filename of CA certificates or None to use defaults.  (JUPYTER_GATEWAY_CA_CERTS env var)
        """,
    )
    ca_certs_env = "JUPYTER_GATEWAY_CA_CERTS"

    @default("ca_certs")
    def _ca_certs_default(self):
        return os.environ.get(self.ca_certs_env)

    http_user = Unicode(
        default_value=None,
        allow_none=True,
        config=True,
        help="""The username for HTTP authentication. (JUPYTER_GATEWAY_HTTP_USER env var)
        """,
    )
    http_user_env = "JUPYTER_GATEWAY_HTTP_USER"

    @default("http_user")
    def _http_user_default(self):
        return os.environ.get(self.http_user_env)

    http_pwd = Unicode(
        default_value=None,
        allow_none=True,
        config=True,
        help="""The password for HTTP authentication.  (JUPYTER_GATEWAY_HTTP_PWD env var)
        """,
    )
    http_pwd_env = "JUPYTER_GATEWAY_HTTP_PWD"

    @default("http_pwd")
    def _http_pwd_default(self):
        return os.environ.get(self.http_pwd_env)

    headers_default_value = "{}"
    headers_env = "JUPYTER_GATEWAY_HEADERS"
    headers = Unicode(
        default_value=headers_default_value,
        allow_none=True,
        config=True,
        help="""Additional HTTP headers to pass on the request.  This value will be converted to a dict.
          (JUPYTER_GATEWAY_HEADERS env var)
        """,
    )

    @default("headers")
    def _headers_default(self):
        return os.environ.get(self.headers_env, self.headers_default_value)

    auth_token = Unicode(
        default_value=None,
        allow_none=True,
        config=True,
        help="""The authorization token used in the HTTP headers. The header will be formatted as:

            {
                'Authorization': '{auth_scheme} {auth_token}'
            }

        (JUPYTER_GATEWAY_AUTH_TOKEN env var)""",
    )
    auth_token_env = "JUPYTER_GATEWAY_AUTH_TOKEN"

    @default("auth_token")
    def _auth_token_default(self):
        return os.environ.get(self.auth_token_env, "")

    auth_scheme = Unicode(
        default_value=None,
        allow_none=True,
        config=True,
        help="""The auth scheme, added as a prefix to the authorization token used in the HTTP headers.
        (JUPYTER_GATEWAY_AUTH_SCHEME env var)""",
    )
    auth_scheme_env = "JUPYTER_GATEWAY_AUTH_SCHEME"

    @default("auth_scheme")
    def _auth_scheme_default(self):
        return os.environ.get(self.auth_scheme_env, "token")

    validate_cert_default_value = True
    validate_cert_env = "JUPYTER_GATEWAY_VALIDATE_CERT"
    validate_cert = Bool(
        default_value=validate_cert_default_value,
        config=True,
        help="""For HTTPS requests, determines if server's certificate should be validated or not.
        (JUPYTER_GATEWAY_VALIDATE_CERT env var)""",
    )

    @default("validate_cert")
    def validate_cert_default(self):
        return bool(
            os.environ.get(self.validate_cert_env, str(self.validate_cert_default_value))
            not in ["no", "false"]
        )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._static_args = {}  # initialized on first use

    env_whitelist_default_value = ""
    env_whitelist_env = "JUPYTER_GATEWAY_ENV_WHITELIST"
    env_whitelist = Unicode(
        default_value=env_whitelist_default_value,
        config=True,
        help="""A comma-separated list of environment variable names that will be included, along with
         their values, in the kernel startup request.  The corresponding `env_whitelist` configuration
         value must also be set on the Gateway server - since that configuration value indicates which
         environmental values to make available to the kernel. (JUPYTER_GATEWAY_ENV_WHITELIST env var)""",
    )

    @default("env_whitelist")
    def _env_whitelist_default(self):
        return os.environ.get(self.env_whitelist_env, self.env_whitelist_default_value)

    gateway_retry_interval_default_value = 1.0
    gateway_retry_interval_env = "JUPYTER_GATEWAY_RETRY_INTERVAL"
    gateway_retry_interval = Float(
        default_value=gateway_retry_interval_default_value,
        config=True,
        help="""The time allowed for HTTP reconnection with the Gateway server for the first time.
            Next will be JUPYTER_GATEWAY_RETRY_INTERVAL multiplied by two in factor of numbers of retries
            but less than JUPYTER_GATEWAY_RETRY_INTERVAL_MAX.
            (JUPYTER_GATEWAY_RETRY_INTERVAL env var)""",
    )

    @default("gateway_retry_interval")
    def gateway_retry_interval_default(self):
        return float(
            os.environ.get(
                "JUPYTER_GATEWAY_RETRY_INTERVAL", self.gateway_retry_interval_default_value
            )
        )

    gateway_retry_interval_max_default_value = 30.0
    gateway_retry_interval_max_env = "JUPYTER_GATEWAY_RETRY_INTERVAL_MAX"
    gateway_retry_interval_max = Float(
        default_value=gateway_retry_interval_max_default_value,
        config=True,
        help="""The maximum time allowed for HTTP reconnection retry with the Gateway server.
            (JUPYTER_GATEWAY_RETRY_INTERVAL_MAX env var)""",
    )

    @default("gateway_retry_interval_max")
    def gateway_retry_interval_max_default(self):
        return float(
            os.environ.get(
                "JUPYTER_GATEWAY_RETRY_INTERVAL_MAX", self.gateway_retry_interval_max_default_value
            )
        )

    gateway_retry_max_default_value = 5
    gateway_retry_max_env = "JUPYTER_GATEWAY_RETRY_MAX"
    gateway_retry_max = Int(
        default_value=gateway_retry_max_default_value,
        config=True,
        help="""The maximum retries allowed for HTTP reconnection with the Gateway server.
            (JUPYTER_GATEWAY_RETRY_MAX env var)""",
    )

    @default("gateway_retry_max")
    def gateway_retry_max_default(self):
        return int(
            os.environ.get("JUPYTER_GATEWAY_RETRY_MAX", self.gateway_retry_max_default_value)
        )

    @property
    def gateway_enabled(self):
        return bool(self.url is not None and len(self.url) > 0)

    # Ensure KERNEL_LAUNCH_TIMEOUT has a default value.
    KERNEL_LAUNCH_TIMEOUT = int(os.environ.get("KERNEL_LAUNCH_TIMEOUT", 40))

    def init_static_args(self):
        """Initialize arguments used on every request.  Since these are static values, we'll
        perform this operation once.

        """
        # Ensure that request timeout and KERNEL_LAUNCH_TIMEOUT are the same, taking the
        #  greater value of the two.
        if self.request_timeout < float(GatewayClient.KERNEL_LAUNCH_TIMEOUT):
            self.request_timeout = float(GatewayClient.KERNEL_LAUNCH_TIMEOUT)
        elif self.request_timeout > float(GatewayClient.KERNEL_LAUNCH_TIMEOUT):
            GatewayClient.KERNEL_LAUNCH_TIMEOUT = int(self.request_timeout)
        # Ensure any adjustments are reflected in env.
        os.environ["KERNEL_LAUNCH_TIMEOUT"] = str(GatewayClient.KERNEL_LAUNCH_TIMEOUT)

        self._static_args["headers"] = json.loads(self.headers)
        if "Authorization" not in self._static_args["headers"].keys():
            self._static_args["headers"].update(
                {"Authorization": "{} {}".format(self.auth_scheme, self.auth_token)}
            )
        self._static_args["connect_timeout"] = self.connect_timeout
        self._static_args["request_timeout"] = self.request_timeout
        self._static_args["validate_cert"] = self.validate_cert
        if self.client_cert:
            self._static_args["client_cert"] = self.client_cert
            self._static_args["client_key"] = self.client_key
            if self.ca_certs:
                self._static_args["ca_certs"] = self.ca_certs
        if self.http_user:
            self._static_args["auth_username"] = self.http_user
        if self.http_pwd:
            self._static_args["auth_password"] = self.http_pwd

    def load_connection_args(self, **kwargs):
        """Merges the static args relative to the connection, with the given keyword arguments.  If statics
        have yet to be initialized, we'll do that here.

        """
        if len(self._static_args) == 0:
            self.init_static_args()

        kwargs.update(self._static_args)
        return kwargs


async def gateway_request(endpoint, **kwargs):
    """Make an async request to kernel gateway endpoint, returns a response """
    client = AsyncHTTPClient()
    kwargs = GatewayClient.instance().load_connection_args(**kwargs)
    try:
        response = await client.fetch(endpoint, **kwargs)
    # Trap a set of common exceptions so that we can inform the user that their Gateway url is incorrect
    # or the server is not running.
    # NOTE: We do this here since this handler is called during the Notebook's startup and subsequent refreshes
    # of the tree view.
    except ConnectionRefusedError as e:
        raise web.HTTPError(
            503,
            "Connection refused from Gateway server url '{}'.  "
            "Check to be sure the Gateway instance is running.".format(
                GatewayClient.instance().url
            ),
        ) from e
    except HTTPError as e:
        # This can occur if the host is valid (e.g., foo.com) but there's nothing there.
        raise web.HTTPError(
            e.code,
            "Error attempting to connect to Gateway server url '{}'.  "
            "Ensure gateway url is valid and the Gateway instance is running.".format(
                GatewayClient.instance().url
            ),
        ) from e
    except gaierror as e:
        raise web.HTTPError(
            404,
            "The Gateway server specified in the gateway_url '{}' doesn't appear to be valid.  "
            "Ensure gateway url is valid and the Gateway instance is running.".format(
                GatewayClient.instance().url
            ),
        ) from e

    return response
