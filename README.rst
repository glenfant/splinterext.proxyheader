=======================
splinterext.proxyheader
=======================

Abstract
========

You too love |splinter| that makes Web functional tests through a real browser
so easy.

Unfortunately, |splinter| has a limited access to the request and response HTTP
headers. This is the consequence of the limitation of the browser drivers
|splinter| relies on. So whatever's the talent of the |splinter| developers,
this issue cannot be closed in a clean fashion as long as these drivers don't
support HTTP headers.

But there is a solution
=======================

This package adds to |splinter| browser the ability to play with HTTP request
and response headers with additional APIs. This is done by instanciating a tests
dedicated proxy on localhost on which the tests browser will rely.

This special proxy will give you the ability to control the HTTP request headers
as well as readind the response headers through additional |splinter| browser
methods.

Don't worry about starting or stopping that proxy. This is completely
transparent: this temporary proxy is built and started when you create your
browser through the legacy API, then stopped and deleted when you invoke the
``quit()`` method or the test script exits.

Using ``splinterext.proxyheader``
=================================

Now, instead of: ::

  from splinter import Browser
  ...
  browser = Browser("whatever", ...)

You will need to write this: ::

  from splinterext.proxyheader import Browser
  ...
  browser = Browser("whatever", ..., use_proxy=3128, ...)
  ...
  # Now you can use ``browser`` as a legacy splinter browser with some adds.

.. admonition:: But...

   The counterpart of this is that your favorite browser setup must include an
   HTTP + HTTPS proxy on localhost, on some available port (say ``3128`` that's
   the default port for proxies, manageable by non root users)

   Firefox profiles manager lets you add named profiles. Read `this
   <http://support.mozilla.org/en-US/kb/profile-manager-create-and-remove-firefox-profiles>`_
   and create a ``splinterproxy`` profile that includes that proxy setup. Then
   your scripts should look like this ::

     from splinterext.proxyheader import Browser
     ...
     browser = Browser("firefox", ..., profile="spliterproxy", ... use_proxy=3128)

Additional API
==============

The ``Browser`` object provided by ``splinterext.proxyheader`` provides these
additional methods :

* set a header with a value ::

    browser.set_request_header(name, value)

* removes a header (fails silently) ::

    browser.remove_request_header(name)

* set a basic authentication token ::

    browser.basic_authenticate(login, password)

* clear an authentication token ::

    browser.basic_anonymize()

* get a response header (``None`` if header not found) ::

    browser.get_response_header(name)

Known issues
============

HTTPS support
  The (poor) proxy does not support https. Pages published by https server won't
  show, pages having sub elements (images, ...) published by https servers will
  be incomplete.

Thread safety
  There are some global objects that inject and capture headers. Playing with
  browsers shared by threads or even threads that control their own browser may
  drive to weird results.

.. |splinter| replace:: splinter
.. _splinter: http://splinter.cobrateam.info/
