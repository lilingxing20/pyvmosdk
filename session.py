# -*- coding:utf-8 -*-

from __future__ import absolute_import

import logging
import ssl
import time
import six

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vmodl, vim

LOG = logging.getLogger(__name__)


class VcenterInfo(object):
    """ 
    The vCenter connection info object.
    """

    def __init__(self, host, user, pwd, port=443, timeout=900):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port
        # Timeout in secs for idle connections in client pool. Use -1 to disable any timeout.
        self.timeout = timeout


class VcenterSession(object):
    """
    Sets up a session with the VC/ESX host.
    """

    def __init__(self, vc_info):
        self.host = vc_info.host
        self.user = vc_info.user
        self.pwd = vc_info.pwd
        self.port = vc_info.port
        self.timeout = vc_info.timeout
        self._sessionManager = None
        self._session_id = None
        self._si = None
        self._create_session()

    def _create_session(self):
        """

        """
        connect_time = 0
        while connect_time < 3:
            try:
                context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                context.verify_mode = ssl.CERT_NONE
                service_instance = SmartConnect(host=self.host,
                                                user=self.user,
                                                pwd=self.pwd,
                                                port=int(self.port),
                                                connectionPoolTimeout=int(
                                                    self.timeout),
                                                sslContext=context)
                self.si = service_instance
                self._sessionManager = service_instance.content.sessionManager
                self._session_id = service_instance.content.sessionManager.currentSession.key
                LOG.debug("The vCenter server (%s) has authenticated." %
                          self.host)
                break
            except vim.fault.InvalidLogin as ex:
                raise Exception(ex.msg)
            except Exception as ex:
                LOG.exception(ex)
                connect_time += 1
                if connect_time == 3:
                    raise Exception("vcenter auth error: %s " % str(ex))
                time.sleep(2)
        return service_instance

    @property
    def is_current_session_active(self):
        """
        Check if current session is active.

        :returns: True if the session is active; False otherwise
        """
        is_active = False
        try:
            is_active = self._sessionManager.SessionIsActive(
                self._session_id, self.user)
        except Exception as ex:
            LOG.debug("Error: %(error)s occurred while checking whether the "
                      "current session: %(session)s is active.",
                      {'error': six.text_type(ex),
                       'session': self._session_id})
        return is_active

    @property
    def service_instance(self):
        """
        vCenter Auth Session.
        """
        if self.is_current_session_active:
            return self._si
        else:
            return self._create_session()

    @property
    def si(self):
        return self.service_instance

    def get_session_id(self):
        try:
            # NOTE: only a successfully authenticated session has a session key aka session id.
            return self.si.content.sessionManager.currentSession.key
        except Exception as ex:
            LOG.exception(ex)
            raise Exception("Get vCenter session id error: %s" % str(ex))

    def disconnect(self):
        if self._si:
            Disconnect(self.si)
    
    def get_vc_version(self):
        """
        Return the dot-separated vCenter version string.
        For example, "6.0.0".
        """
        return self.si.content.about.version