#!/usr/bin/python3
"""
Module for interfacing with the nanofilm LabVIEW applications.
"""

__author__ = 'Falk Ziegler'
__credits__ = ['Falk Ziegler']
__maintainer__ = 'Jan-Henrik Quast'
__email__ = 'jqu@accurion.com'

__all__ = ['IPConnection']

import socket
import time
import struct
from functools import partial
import json


class IPConnection:
    """
    Class for ipconnections into the nanofilm LabVIEW applications.
    """
    # LV strings are not utf-8, but extended ascii !
    ENCODING = 'ISO-8859-1'
    
    class Wrapper:
        """
        Wrapper class...
        """
        def __init__(self, name):
            self.name = name

    def __init__(self, address, port):
        """
        Creates an IP connection object to communicate into the nanofilm
        LabVIEW applications.
        """
        self._sockets = {'DEFAULT': None, 'INTERRUPT': None}
        self._host = address
        self._port = port
        self._wrapped_instances = {}
        
        for socket_id in self._sockets.keys():
            self._connect(socket_id)
        
        for name in self._call('__init__'):
            setattr(self, name, partial(self._call, name))
    
    def __enter__(self):
        """
        For context managers.
        """
        return self
    
    def __exit__(self, type, value, traceback):
        """
        For context managers.
        """
        self.close()
    
    def _connect(self, socket_id):
        """
        Create a socket object and connect it to the remote application.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(0.5)
            s.connect((self._host, self._port))
        except:
            s.close()
            raise
        self._sockets[socket_id] = s
        self._call('python@{0}:{1}'.format(*s.getsockname()), socket_id=socket_id, header=False, synchronous=False)
    
    def _disconnect(self, socket_id):
        """
        Disconnects from a socket object.
        """
        sock = self._sockets.get(socket_id)
        if sock is not None:
            self._sockets[socket_id] = None
            try:
                sock.shutdown(socket.SHUT_RDWR)
            finally:
                sock.close()
    
    def _interrupt(self):
        """
        Tries to call the external __interrupt__ method.
        """
        try:
            self._call('__close__', socket_id='INTERRUPT', synchronous=True)
        except:
            pass
    
    def close(self):
        """
        Closes the previously established connection to the application.
        """
        for instance in [instance['reference'] for instance in self._wrapped_instances.values()]:
            self._delete(instance)
        self._interrupt()
        for socket_id in self._sockets.keys():
            self._disconnect(socket_id)
    
    @staticmethod
    def _pack(data):
        """
        Static helper method to pack the data in reference to the protocol.
        """
        if not isinstance(data, bytes):
            data = bytes(data, IPConnection.ENCODING)
        return struct.pack('>I', len(data)) + data
    
    def _call(self, cmd, *args, socket_id='DEFAULT', header=True, synchronous=True):
        """
        Internal method for the data transmission.
        """
        sock = self._sockets.get(socket_id)
        if sock is not None:
            data = struct.pack('>IIbb', 123, 123, 1, int(synchronous)) if header else b''
            data += self._pack(cmd)
            for arg in args:
                # check if the argument is an object of the Wrapper class
                if type(arg) == IPConnection.Wrapper:
                    # use the name attribute of the object as argument
                    arg = arg.name
                elif type(arg) == dict:
                    # pass dict as json string. CMD should expect LV type "Cluster"
                    arg = json.dumps(arg)
                else:
                    arg = repr(arg)

                data += self._pack(arg)
            
            try:
                sock.sendall(self._pack(data))
                data = b''
                if synchronous:
                    payload = struct.unpack('>I', self._recv_from_socket(sock, struct.calcsize('>I')))[0]
                    data +=  self._recv_from_socket(sock, payload)
                
            except (Exception, KeyboardInterrupt) as e:
                if socket_id == 'DEFAULT':
                    self._interrupt()
                    self._disconnect(socket_id)
                    if not isinstance(e, ConnectionError):
                        self._connect(socket_id)
                raise e
                
            if data:
                # Skip the complete header here.    
                data = data[struct.calcsize('>IIbb'):].decode(IPConnection.ENCODING)
                # Use of 'eval' is very strange so we have to think about an alternative
                # way for the data transmission (BSON, JSON)
                status, source, data = eval(data, {'__builtins__' : None}, {})
                if status:
                    raise RuntimeError(source)
                return data
    
    @staticmethod
    def _recv_from_socket(sock, n):
        """
        Receives data of size n from the socket defined by sock.
        """
        data = b''
        while len(data) < n:
            try:
                data += sock.recv(n - len(data))
                if not data:
                    raise ConnectionError
            except socket.timeout:
                continue
        else:
            return data
    
    def _new(self, name, cls=None):
        """
        Creates an application instance and its corresponding Python object.
        Leave cls=None if the application instance already exists and to create
        only an correspondig Python object.
        """
        self._wrapped_instances[name] = dict([('reference', IPConnection.Wrapper(name)), ('created_new', cls is not None)])
        if cls is not None: 
            self._create_object(name, cls)
        call_function = lambda _event, *params: self._call('_call_object', name, _event, *params)
        for event in call_function('_get_events')[0]:
            if not event.startswith('_'):
                setattr(self._wrapped_instances[name]['reference'], event, partial(call_function, event))
        return self._wrapped_instances[name]['reference']
    
    def _delete(self, instance, force=False):
        """
        Deletes the application instance and the correspondig Python object.
        The parameter 'instance' can be the Python object or the instance name string.
        """
        if isinstance(instance, IPConnection.Wrapper):
            instance = instance.name
        attrs = self._wrapped_instances.get(instance, {})
        if attrs.get('created_new', False) or force:
            self._delete_object(instance)
        self._wrapped_instances.pop(instance, None)
