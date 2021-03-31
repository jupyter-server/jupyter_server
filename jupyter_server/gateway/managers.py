# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import datetime
import json
import os
import websocket

from jupyter_client.asynchronous.client import AsyncKernelClient
from jupyter_client.clientabc import KernelClientABC
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client.manager import AsyncKernelManager
from jupyter_client.managerabc import KernelManagerABC

from logging import Logger
from queue import Queue
from threading import Thread
from tornado import web
from tornado.escape import json_encode, json_decode, url_escape, utf8
from tornado.httpclient import HTTPClient, HTTPError
from traitlets import Instance, DottedObjectName, Type

from .gateway_client import GatewayClient, gateway_request
from ..services.kernels.kernelmanager import AsyncMappingKernelManager
from ..services.sessions.sessionmanager import SessionManager
from ..utils import url_path_join, ensure_async


class GatewayKernelManagers(AsyncMappingKernelManager):
    """Kernel manager that supports remote kernels hosted by Jupyter Kernel or Enterprise Gateway."""

    # We'll maintain our own set of kernel ids
    _kernels = {}

    def __init__(self, **kwargs):
        super(GatewayKernelManagers, self).__init__(**kwargs)
        self.base_endpoint = url_path_join(GatewayClient.instance().url, GatewayClient.instance().kernels_endpoint)

    def __contains__(self, kernel_id):
        return kernel_id in self._kernels

    def remove_kernel(self, kernel_id):
        """Complete override since we want to be more tolerant of missing keys """
        try:
            return self._kernels.pop(kernel_id)
        except KeyError:
            pass

    def _get_kernel_endpoint_url(self, kernel_id=None):
        """Builds a url for the kernels endpoint

        Parameters
        ----------
        kernel_id: kernel UUID (optional)
        """
        if kernel_id:
            return url_path_join(self.base_endpoint, url_escape(str(kernel_id)))

        return self.base_endpoint

    async def start_kernel(self, kernel_id=None, path=None, **kwargs):
        """Start a kernel for a session and return its kernel_id.

        Parameters
        ----------
        kernel_id : uuid
            The uuid to associate the new kernel with. If this
            is not None, this kernel will be persistent whenever it is
            requested.
        path : API path
            The API path (unicode, '/' delimited) for the cwd.
            Will be transformed to an OS path relative to root_dir.
        """
        self.log.info(f"Request start kernel: kernel_id={kernel_id}, path='{path}'")

        if kernel_id is None:
            if path is not None:
                kwargs['cwd'] = self.cwd_for_path(path)
            kernel_name = kwargs.get('kernel_name', 'python3')
            kernel_url = self._get_kernel_endpoint_url()
            self.log.debug(f"Request new kernel at: {kernel_url}")

            # Let KERNEL_USERNAME take precedent over http_user config option.
            if os.environ.get('KERNEL_USERNAME') is None and GatewayClient.instance().http_user:
                os.environ['KERNEL_USERNAME'] = GatewayClient.instance().http_user

            kernel_env = {k: v for (k, v) in dict(os.environ).items() if k.startswith('KERNEL_')
                        or k in GatewayClient.instance().env_whitelist.split(",")}

            # Convey the full path to where this notebook file is located.
            if path is not None and kernel_env.get('KERNEL_WORKING_DIR') is None:
                kernel_env['KERNEL_WORKING_DIR'] = kwargs['cwd']

            json_body = json_encode({'name': kernel_name, 'env': kernel_env})

            response = await gateway_request(kernel_url, method='POST', body=json_body)
            kernel = json_decode(response.body)
            kernel_id = kernel['id']
            self.log.info(f"Kernel started: {kernel_id}")
            self.log.debug(f"Kernel args: {kwargs}")
        else:
            kernel = await self.get_kernel(kernel_id)
            kernel_id = kernel['id']
            self.log.info(f"Using existing kernel: {kernel_id}")

        self._kernels[kernel_id] = kernel
        return kernel_id

    async def get_kernel(self, kernel_id=None, **kwargs):
        """Get kernel for kernel_id.

        Parameters
        ----------
        kernel_id : uuid
            The uuid of the kernel.
        """
        kernel_url = self._get_kernel_endpoint_url(kernel_id)
        self.log.debug(f"Request kernel at: {kernel_url}")
        try:
            response = await gateway_request(kernel_url, method='GET')
        except web.HTTPError as error:
            if error.status_code == 404:
                self.log.warn(f"Kernel not found at: {kernel_url}")
                self.remove_kernel(kernel_id)
                kernel = None
            else:
                raise
        else:
            kernel = json_decode(response.body)
            # Only update our models if we already know about this kernel
            if kernel_id in self._kernels:
                self._kernels[kernel_id] = kernel
                self.log.debug(f"Kernel retrieved: {kernel}")
            else:
                self.log.warning(f"Kernel '{kernel_id}' is not managed by this instance.")
                kernel = None
        return kernel

    async def kernel_model(self, kernel_id):
        """Return a dictionary of kernel information described in the
        JSON standard model.

        Parameters
        ----------
        kernel_id : uuid
            The uuid of the kernel.
        """
        model = await self.get_kernel(kernel_id)
        return model

    async def list_kernels(self, **kwargs):
        """Get a list of kernels."""
        kernel_url = self._get_kernel_endpoint_url()
        self.log.debug(f"Request list kernels: {kernel_url}")
        response = await gateway_request(kernel_url, method='GET')
        kernels = json_decode(response.body)
        # Only update our models if we already know about the kernels
        self._kernels = {x['id']: x for x in kernels if x['id'] in self._kernels}
        return list(self._kernels.values())

    async def shutdown_kernel(self, kernel_id, now=False, restart=False):
        """Shutdown a kernel by its kernel uuid.

        Parameters
        ==========
        kernel_id : uuid
            The id of the kernel to shutdown.
        now : bool
            Shutdown the kernel immediately (True) or gracefully (False)
        restart : bool
            The purpose of this shutdown is to restart the kernel (True)
        """
        kernel_url = self._get_kernel_endpoint_url(kernel_id)
        self.log.debug(f"Request shutdown kernel at: {kernel_url}")
        response = await gateway_request(kernel_url, method='DELETE')
        self.log.debug(f"Shutdown kernel response: {response.code} {response.reason}")
        self.remove_kernel(kernel_id)

    async def restart_kernel(self, kernel_id, now=False, **kwargs):
        """Restart a kernel by its kernel uuid.

        Parameters
        ==========
        kernel_id : uuid
            The id of the kernel to restart.
        """
        kernel_url = self._get_kernel_endpoint_url(kernel_id) + '/restart'
        self.log.debug(f"Request restart kernel at: {kernel_url}")
        response = await gateway_request(kernel_url, method='POST', body=json_encode({}))
        self.log.debug(f"Restart kernel response: {response.code} {response.reason}")

    async def interrupt_kernel(self, kernel_id, **kwargs):
        """Interrupt a kernel by its kernel uuid.

        Parameters
        ==========
        kernel_id : uuid
            The id of the kernel to interrupt.
        """
        kernel_url = self._get_kernel_endpoint_url(kernel_id) + '/interrupt'
        self.log.debug(f"Request interrupt kernel at: {kernel_url}")
        response = await gateway_request(kernel_url, method='POST', body=json_encode({}))
        self.log.debug(f"Interrupt kernel response: {response.code} {response.reason}")

    def shutdown_all(self, now=False):
        """Shutdown all kernels."""
        # Note: We have to make this sync because the NotebookApp does not wait for async.
        shutdown_kernels = []
        kwargs = {'method': 'DELETE'}
        kwargs = GatewayClient.instance().load_connection_args(**kwargs)
        client = HTTPClient()
        for kernel_id in self._kernels:
            kernel_url = self._get_kernel_endpoint_url(kernel_id)
            self.log.debug(f"Request delete kernel at: {kernel_url}")
            try:
                response = client.fetch(kernel_url, **kwargs)
            except HTTPError:
                pass
            else:
                self.log.debug(f"Delete kernel response: {response.code} {response.reason}")
            shutdown_kernels.append(kernel_id)  # avoid changing dict size during iteration
        client.close()
        for kernel_id in shutdown_kernels:
            self.remove_kernel(kernel_id)


class GatewayKernelSpecManager(KernelSpecManager):

    def __init__(self, **kwargs):
        super(GatewayKernelSpecManager, self).__init__(**kwargs)
        base_endpoint = url_path_join(GatewayClient.instance().url,
                                      GatewayClient.instance().kernelspecs_endpoint)

        self.base_endpoint = GatewayKernelSpecManager._get_endpoint_for_user_filter(base_endpoint)
        self.base_resource_endpoint = url_path_join(GatewayClient.instance().url,
                                                    GatewayClient.instance().kernelspecs_resource_endpoint)

    @staticmethod
    def _get_endpoint_for_user_filter(default_endpoint):
        kernel_user = os.environ.get('KERNEL_USERNAME')
        if kernel_user:
            return '?user='.join([default_endpoint, kernel_user])
        return default_endpoint

    def _get_kernelspecs_endpoint_url(self, kernel_name=None):
        """Builds a url for the kernels endpoint

        Parameters
        ----------
        kernel_name: kernel name (optional)
        """
        if kernel_name:
            return url_path_join(self.base_endpoint, url_escape(kernel_name))

        return self.base_endpoint

    async def get_all_specs(self):
        fetched_kspecs = await self.list_kernel_specs()

        # get the default kernel name and compare to that of this server.
        # If different log a warning and reset the default.  However, the
        # caller of this method will still return this server's value until
        # the next fetch of kernelspecs - at which time they'll match.
        km = self.parent.kernel_manager
        remote_default_kernel_name = fetched_kspecs.get('default')
        if remote_default_kernel_name != km.default_kernel_name:
            self.log.info(f"Default kernel name on Gateway server ({remote_default_kernel_name}) differs from "
                          f"Notebook server ({km.default_kernel_name}).  Updating to Gateway server's value.")
            km.default_kernel_name = remote_default_kernel_name

        remote_kspecs = fetched_kspecs.get('kernelspecs')
        return remote_kspecs

    async def list_kernel_specs(self):
        """Get a list of kernel specs."""
        kernel_spec_url = self._get_kernelspecs_endpoint_url()
        self.log.debug(f"Request list kernel specs at: {kernel_spec_url}")
        response = await gateway_request(kernel_spec_url, method='GET')
        kernel_specs = json_decode(response.body)
        return kernel_specs

    async def get_kernel_spec(self, kernel_name, **kwargs):
        """Get kernel spec for kernel_name.

        Parameters
        ----------
        kernel_name : str
            The name of the kernel.
        """
        kernel_spec_url = self._get_kernelspecs_endpoint_url(kernel_name=str(kernel_name))
        self.log.debug(f"Request kernel spec at: {kernel_spec_url}")
        try:
            response = await gateway_request(kernel_spec_url, method='GET')
        except web.HTTPError as error:
            if error.status_code == 404:
                # Convert not found to KeyError since that's what the Notebook handler expects
                # message is not used, but might as well make it useful for troubleshooting
                raise KeyError(
                    'kernelspec {kernel_name} not found on Gateway server at: {gateway_url}'.
                    format(kernel_name=kernel_name, gateway_url=GatewayClient.instance().url)
                ) from error
            else:
                raise
        else:
            kernel_spec = json_decode(response.body)

        return kernel_spec

    async def get_kernel_spec_resource(self, kernel_name, path):
        """Get kernel spec for kernel_name.

        Parameters
        ----------
        kernel_name : str
            The name of the kernel.
        path : str
            The name of the desired resource
        """
        kernel_spec_resource_url = url_path_join(self.base_resource_endpoint, str(kernel_name), str(path))
        self.log.debug(f"Request kernel spec resource '{path}' at: {kernel_spec_resource_url}")
        try:
            response = await gateway_request(kernel_spec_resource_url, method='GET')
        except web.HTTPError as error:
            if error.status_code == 404:
                kernel_spec_resource = None
            else:
                raise
        else:
            kernel_spec_resource = response.body
        return kernel_spec_resource


class GatewaySessionManager(SessionManager):
    kernel_manager = Instance('jupyter_server.gateway.managers.GatewayKernelManagers')

    async def kernel_culled(self, kernel_id):
        """Checks if the kernel is still considered alive and returns true if its not found. """
        kernel = await self.kernel_manager.get_kernel(kernel_id)
        return kernel is None


"""KernelManager class to manage a kernel running on a Gateway Server via the REST API"""


class GatewayKernelManager(AsyncKernelManager):
    """Manages a single kernel remotely via a Gateway Server. """

    kernel_id = None
    kernel = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_endpoint = url_path_join(GatewayClient.instance().url, GatewayClient.instance().kernels_endpoint)
        self.kernel = None

    def _get_kernel_endpoint_url(self, kernel_id=None):
        """Builds a url for the kernels endpoint

        Parameters
        ----------
        kernel_id: kernel UUID (optional)
        """
        if kernel_id:
            return url_path_join(self.base_endpoint, url_escape(str(kernel_id)))

        return self.base_endpoint

    @property
    def has_kernel(self):
        """Has a kernel been started that we are managing."""
        return self.kernel is not None

    client_class = DottedObjectName('jupyter_server.gateway.managers.GatewayKernelClient')
    client_factory = Type(klass='jupyter_server.gateway.managers.GatewayKernelClient')

    # --------------------------------------------------------------------------
    # create a Client connected to our Kernel
    # --------------------------------------------------------------------------

    def client(self, **kwargs):
        """Create a client configured to connect to our kernel"""
        kw = {}
        kw.update(self.get_connection_info(session=True))
        kw.update(dict(
            connection_file=self.connection_file,
            parent=self,
        ))
        kw['kernel_id'] = self.kernel_id

        # add kwargs last, for manual overrides
        kw.update(kwargs)
        return self.client_factory(**kw)

    async def get_kernel_model(self, kernel_id):
        """Get kernel model from gateway server for kernel_id.

        Parameters
        ----------
        kernel_id : uuid
            The uuid of the kernel.
        """
        kernel_url = self._get_kernel_endpoint_url(kernel_id)
        self.log.debug("Request kernel at: %s" % kernel_url)
        try:
            response = await gateway_request(kernel_url, method='GET')
        except web.HTTPError as error:
            if error.status_code == 404:
                self.log.warning("Kernel not found at: %s" % kernel_url)
                kernel = None
            else:
                raise
        else:
            kernel = json_decode(response.body)
        self.log.debug("Kernel retrieved: %s" % kernel)
        return kernel

    # --------------------------------------------------------------------------
    # Kernel management
    # --------------------------------------------------------------------------

    async def start_kernel(self, **kwargs):
        """Starts a kernel via HTTP in an asynchronous manner.

        Parameters
        ----------
        `**kwargs` : optional
             keyword arguments that are passed down to build the kernel_cmd
             and launching the kernel (e.g. Popen kwargs).
        """
        kernel_id = kwargs.get('kernel_id')

        if kernel_id is None:
            kernel_name = kwargs.get('kernel_name', 'python3')
            kernel_url = self._get_kernel_endpoint_url()
            self.log.debug("Request new kernel at: %s" % kernel_url)

            # Let KERNEL_USERNAME take precedent over http_user config option.
            if os.environ.get('KERNEL_USERNAME') is None and GatewayClient.instance().http_user:
                os.environ['KERNEL_USERNAME'] = GatewayClient.instance().http_user

            kernel_env = {k: v for (k, v) in dict(os.environ).items() if k.startswith('KERNEL_') or
                          k in GatewayClient.instance().env_whitelist.split(",")}

            # Add any env entries in this request
            kernel_env.update(kwargs.get('env'))

            # Convey the full path to where this notebook file is located.
            if kwargs.get('cwd') is not None and kernel_env.get('KERNEL_WORKING_DIR') is None:
                kernel_env['KERNEL_WORKING_DIR'] = kwargs['cwd']

            json_body = json_encode({'name': kernel_name, 'env': kernel_env})

            response = await gateway_request(kernel_url, method='POST', body=json_body)
            self.kernel = json_decode(response.body)
            self.kernel_id = self.kernel['id']
            self.log.info("GatewayKernelManager started kernel: {}, args: {}".format(self.kernel_id, kwargs))
        else:
            self.kernel = await self.get_kernel_model(kernel_id)
            self.kernel_id = self.kernel['id']
            self.log.info("GatewayKernelManager using existing kernel: {}".format(self.kernel_id))

    async def shutdown_kernel(self, now=False, restart=False):
        """Attempts to stop the kernel process cleanly via HTTP. """

        if self.has_kernel:
            kernel_url = self._get_kernel_endpoint_url(self.kernel_id)
            self.log.debug("Request shutdown kernel at: %s", kernel_url)
            response = await gateway_request(kernel_url, method='DELETE')
            self.log.debug("Shutdown kernel response: %d %s", response.code, response.reason)

    async def restart_kernel(self, **kw):
        """Restarts a kernel via HTTP.  """
        if self.has_kernel:
            kernel_url = self._get_kernel_endpoint_url(self.kernel_id) + '/restart'
            self.log.debug("Request restart kernel at: %s", kernel_url)
            response = await gateway_request(kernel_url, method='POST', body=json_encode({}))
            self.log.debug("Restart kernel response: %d %s", response.code, response.reason)

    async def interrupt_kernel(self):
        """Interrupts the kernel via an HTTP request. """
        if self.has_kernel:
            kernel_url = self._get_kernel_endpoint_url(self.kernel_id) + '/interrupt'
            self.log.debug("Request interrupt kernel at: %s", kernel_url)
            response = await gateway_request(kernel_url, method='POST', body=json_encode({}))
            self.log.debug("Interrupt kernel response: %d %s", response.code, response.reason)

    async def is_alive(self):
        """Is the kernel process still running?"""
        if self.has_kernel:
            # Go ahead and issue a request to get the kernel
            self.kernel = await self.get_kernel_model(self.kernel_id)
            return True
        else:  # we don't have a kernel
            return False

    def cleanup_resources(self, restart=False):
        """Clean up resources when the kernel is shut down"""
        pass


KernelManagerABC.register(GatewayKernelManager)


class ChannelQueue(Queue):

    channel_name: str = None

    def __init__(self, channel_name: str, channel_socket: websocket.WebSocket, log: Logger):
        super().__init__()
        self.channel_name = channel_name
        self.channel_socket = channel_socket
        self.log = log

    async def get_msg(self, *args, **kwargs) -> dict:
        timeout = kwargs.get('timeout', 1)
        msg = self.get(timeout=timeout)
        self.log.debug("Received message on channel: {}, msg_id: {}, msg_type: {}".
                       format(self.channel_name, msg['msg_id'], msg['msg_type'] if msg else 'null'))
        self.task_done()
        return msg

    def send(self, msg: dict) -> None:
        message = json.dumps(msg, default=ChannelQueue.serialize_datetime).replace("</", "<\\/")
        self.log.debug("Sending message on channel: {}, msg_id: {}, msg_type: {}".
                       format(self.channel_name, msg['msg_id'], msg['msg_type'] if msg else 'null'))
        self.channel_socket.send(message)

    @staticmethod
    def serialize_datetime(dt):
        if isinstance(dt, (datetime.date, datetime.datetime)):
            return dt.timestamp()

    def start(self) -> None:
        pass

    def stop(self) -> None:
        if not self.empty():
            # If unprocessed messages are detected, drain the queue collecting non-status
            # messages.  If any remain that are not 'shutdown_reply' and this is not iopub
            # go ahead and issue a warning.
            msgs = []
            while self.qsize():
                msg = self.get_nowait()
                if msg['msg_type'] != 'status':
                    msgs.append(msg['msg_type'])
            if self.channel_name == 'iopub' and 'shutdown_reply' in msgs:
                return
            if len(msgs):
                self.log.warning("Stopping channel '{}' with {} unprocessed non-status messages: {}.".
                                 format(self.channel_name, len(msgs), msgs))

    def is_alive(self) -> bool:
        return self.channel_socket is not None


class HBChannelQueue(ChannelQueue):

    def is_beating(self) -> bool:
        # Just use the is_alive status for now
        return self.is_alive()


class GatewayKernelClient(AsyncKernelClient):
    """Communicates with a single kernel indirectly via a websocket to a gateway server.

    There are five channels associated with each kernel:

    * shell: for request/reply calls to the kernel.
    * iopub: for the kernel to publish results to frontends.
    * hb: for monitoring the kernel's heartbeat.
    * stdin: for frontends to reply to raw_input calls in the kernel.
    * control: for kernel management calls to the kernel.

    The messages that can be sent on these channels are exposed as methods of the
    client (KernelClient.execute, complete, history, etc.). These methods only
    send the message, they don't wait for a reply. To get results, use e.g.
    :meth:`get_shell_msg` to fetch messages from the shell channel.
    """

    # flag for whether execute requests should be allowed to call raw_input:
    allow_stdin = False
    _channels_stopped = False
    _channel_queues = {}

    def __init__(self, **kwargs):
        super(GatewayKernelClient, self).__init__(**kwargs)
        self.kernel_id = kwargs['kernel_id']
        self.channel_socket = None
        self.response_router = None

    # --------------------------------------------------------------------------
    # Channel management methods
    # --------------------------------------------------------------------------

    async def start_channels(self, shell=True, iopub=True, stdin=True, hb=True, control=True):
        """Starts the channels for this kernel.

        For this class, we establish a websocket connection to the destination
        and setup the channel-based queues on which applicable messages will
        be posted.
        """

        ws_url = url_path_join(
            GatewayClient.instance().ws_url,
            GatewayClient.instance().kernels_endpoint, url_escape(self.kernel_id), 'channels')
        # Gather cert info in case where ssl is desired...
        ssl_options = dict()
        ssl_options['ca_certs'] = GatewayClient.instance().ca_certs
        ssl_options['certfile'] = GatewayClient.instance().client_cert
        ssl_options['keyfile'] = GatewayClient.instance().client_key

        self.channel_socket = websocket.create_connection(ws_url,
                                                          timeout=GatewayClient.instance().KERNEL_LAUNCH_TIMEOUT,
                                                          enable_multithread=True,
                                                          sslopt=ssl_options)
        self.response_router = Thread(target=self._route_responses)
        self.response_router.start()

        await ensure_async(super().start_channels(shell=shell, iopub=iopub, stdin=stdin, hb=hb, control=control))

    def stop_channels(self):
        """Stops all the running channels for this kernel.

        For this class, we close the websocket connection and destroy the
        channel-based queues.
        """
        super().stop_channels()
        self._channels_stopped = True
        self.log.debug("Closing websocket connection")

        self.channel_socket.close()
        self.response_router.join()

        if self._channel_queues:
            self._channel_queues.clear()
            self._channel_queues = None

    # Channels are implemented via a ChannelQueue that is used to send and receive messages

    @property
    def shell_channel(self):
        """Get the shell channel object for this kernel."""
        if self._shell_channel is None:
            self.log.debug("creating shell channel queue")
            self._shell_channel = ChannelQueue('shell', self.channel_socket, self.log)
            self._channel_queues['shell'] = self._shell_channel
        return self._shell_channel

    @property
    def iopub_channel(self):
        """Get the iopub channel object for this kernel."""
        if self._iopub_channel is None:
            self.log.debug("creating iopub channel queue")
            self._iopub_channel = ChannelQueue('iopub', self.channel_socket, self.log)
            self._channel_queues['iopub'] = self._iopub_channel
        return self._iopub_channel

    @property
    def stdin_channel(self):
        """Get the stdin channel object for this kernel."""
        if self._stdin_channel is None:
            self.log.debug("creating stdin channel queue")
            self._stdin_channel = ChannelQueue('stdin', self.channel_socket, self.log)
            self._channel_queues['stdin'] = self._stdin_channel
        return self._stdin_channel

    @property
    def hb_channel(self):
        """Get the hb channel object for this kernel."""
        if self._hb_channel is None:
            self.log.debug("creating hb channel queue")
            self._hb_channel = HBChannelQueue('hb', self.channel_socket, self.log)
            self._channel_queues['hb'] = self._hb_channel
        return self._hb_channel

    @property
    def control_channel(self):
        """Get the control channel object for this kernel."""
        if self._control_channel is None:
            self.log.debug("creating control channel queue")
            self._control_channel = ChannelQueue('control', self.channel_socket, self.log)
            self._channel_queues['control'] = self._control_channel
        return self._control_channel

    def _route_responses(self):
        """
        Reads responses from the websocket and routes each to the appropriate channel queue based
        on the message's channel.  It does this for the duration of the class's lifetime until the
        channels are stopped, at which time the socket is closed (unblocking the router) and
        the thread terminates.  If shutdown happens to occur while processing a response (unlikely),
        termination takes place via the loop control boolean.
        """
        try:
            while not self._channels_stopped:
                raw_message = self.channel_socket.recv()
                if not raw_message:
                    break
                response_message = json_decode(utf8(raw_message))
                channel = response_message['channel']
                self._channel_queues[channel].put_nowait(response_message)

        except websocket.WebSocketConnectionClosedException:
            pass  # websocket closure most likely due to shutdown

        except BaseException as be:
            if not self._channels_stopped:
                self.log.warning('Unexpected exception encountered ({})'.format(be))

        self.log.debug('Response router thread exiting...')


KernelClientABC.register(GatewayKernelClient)
