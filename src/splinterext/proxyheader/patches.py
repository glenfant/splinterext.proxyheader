# -*- coding: utf-8 -*-
# $Id$
"""Additional methods to the Browser"""
import base64
from splinter.driver.webdriver import BaseWebDriver
from utils import ParentMonkeyPatch
import proxy


class NewBaseWebDriver(BaseWebDriver):
    __metaclass__ = ParentMonkeyPatch

    def set_request_header(self, name, value):
        """Additional or changed request header
        """
        proxy.custom_headers.set_header(name, value)
        return

    def unset_request_header(self, name):
        """Remove extra header or use "natural" header
        """
        proxy.custom_headers.unset_header(name)
        return

    def capture_response_headers(self):
        """Will (re)capture response headers of nex HTTP response
        """
        proxy.custom_headers.capture_response_headers()

    def get_response_header(self, name):
        """Get header from last captured response
        None if not found
        """
        return proxy.custom_headers.get_response_header(name)

    def basic_authenticate(self, login, password):
        """Authenticates the user against a Basic Authentication request
        """
        basic_auth = 'Basic {0}'.format(
            base64.encodestring('{0}:{1}'.format(login, password))
        )
        self.set_request_header('Authorization', basic_auth)
        return

    def basic_anonymize(self):
        """Cancels basic_authenticate
        """
        self.unset_request_header('Authorization')
        return

    def quit(self):
        self.__previous_quit()
        proxy.proxy_controller.stop()
        return



try:
    from splinter.driver.zopetestbrowser import ZopeTestBrowser


    class NewZopeTestBrowser(ZopeTestBrowser):
        __metaclass__ = ParentMonkeyPatch

        def set_request_header(self, name, value):
            """Additional or changed request header
            """
            return

        def unset_request_header(self, name):
            """Remove extra header or use "natural" header
            """
            return

        def capture_response_headers(self):
            """Will (re)capture response headers of nex HTTP response
            """
            return

        def get_response_header(self, name):
            """Get header from last captured response
            None if not found
            """
            return

        # Gheee: can't make a mixin class for basic_authenticate
        # and basic_anonymize due to the applied metaclass
        def basic_authenticate(self, login, password):
            """Authenticates the user against a Basic Authentication request
            """
            basic_auth = 'Basic {0}'.format(
                base64.encodestring('{0}:{1}'.format(login, password))
            )
            self.set_request_header('Authorization', basic_auth)
            return

        def basic_anonymize(self):
            """Cancels basic_authenticate
            """
            self.unset_request_header('Authorization')
            return

except ImportError:
    pass
