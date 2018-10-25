"""Test serialize/deserialize messages with buffers"""

import os

from jupyter_protocol.messages import Message
from jupyter_server.services.kernels.ws_serialize import (
    serialize_message, deserialize_message
)

def test_serialize_json():
    msg = Message.from_type('data_pub', content={'a': 'b'})
    smsg = serialize_message(msg, 'iopub')
    assert isinstance(smsg, str)

def test_serialize_binary():
    msg = Message.from_type('data_pub', content={'a': 'b'})
    msg.buffers = [memoryview(os.urandom(3)) for i in range(3)]
    bmsg = serialize_message(msg, 'iopub')
    assert isinstance(bmsg, bytes)

def test_deserialize_json():
    msg = Message.from_type('data_pub', content={'a': 'b'})
    smsg = serialize_message(msg, 'iopub')
    print("Serialised: ", smsg)
    msg_dict = msg.make_dict()
    msg_dict['channel'] = 'iopub'
    msg_dict['buffers'] = []

    msg2 = deserialize_message(smsg)
    assert msg2 == msg_dict

def test_deserialize_binary():
    msg = Message.from_type('data_pub', content={'a': 'b'})
    msg.buffers = [memoryview(os.urandom(3)) for i in range(3)]
    bmsg = serialize_message(msg, 'iopub')
    msg_dict = msg.make_dict()
    msg_dict['channel'] = 'iopub'
    msg_dict['buffers'] = msg.buffers

    msg2 = deserialize_message(bmsg)
    assert msg2 == msg_dict
