# -*- coding: utf-8 -*-
"""splinterext.proxyheader"""

import atexit
from splinter import Browser as BaseBrowser
from proxy import proxy_controller
import patches

NOT_SUPPORTED_DRIVERS = ['zope.testbrowser']


def Browser(driver_name="firefox", *args, **kwargs):
    """Our replacement for the legacy splinter.Browser
    Basically, it **is** a splinter.Browser
    """
    global proxy_controller
    use_proxy = kwargs.get('use_proxy', None)
    if use_proxy is not None:
        del kwargs['use_proxy']
    if (driver_name not in NOT_SUPPORTED_DRIVERS) and (use_proxy is not None):
        # Supposed to be an integer port as typically 3128
        use_proxy = int(use_proxy)
        # Run the proxy
        proxy_controller.start(use_proxy)
    return BaseBrowser(driver_name=driver_name, *args, **kwargs)
