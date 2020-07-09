# -*- coding:utf-8 -*-
"""
@file
@brief This file defines a simple local server delivering generating documentation.
"""
import sys
import os
import subprocess
import copy
import datetime
try:
    from urllib.parse import urlparse, parse_qs
except ImportError:  # pragma: no cover
    from urlparse import urlparse, parse_qs
from threading import Thread
try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:  # pragma: no cover
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

if __name__ == "__main__":  # pragma: no cover
    path_ = os.path.normpath(os.path.abspath(
        os.path.join(os.path.split(__file__)[0], "..", "..", "..", "src")))
    if path_ not in sys.path:
        sys.path.append(path_)
    path_ = os.path.normpath(os.path.abspath(os.path.join(os.path.split(__file__)[0],
                                                          "..", "..", "..", "..", "pyquickhelper", "src")))
    if path_ not in sys.path:
        sys.path.append(path_)
    from pyquickhelper.loghelper import fLOG, get_url_content
else:
    from ..loghelper.flog import fLOG
    from ..loghelper.url_helper import get_url_content


class DocumentationHandler(BaseHTTPRequestHandler):

    """
    Define a simple handler used by HTTPServer,
    it just serves local content.

    """

    mappings = {"__fetchurl__": "http://",
                "__shutdown__": "shut://",
                }

    html_header = """
            <?xml version="1.0" encoding="utf-8"?>
            <html>
            <head>
            <title>%s</title>
            </head>
            <body>
            """.replace("            ", "")

    html_footer = """
            </body>
            </html>
            """.replace("            ", "")

    cache = {}
    cache_attributes = {}
    cache_refresh = datetime.timedelta(1)

    def LOG(self, *args, **kwargs):
        """
        logging function
        """
        fLOG(*args, **kwargs)

    @staticmethod
    def add_mapping(key, value):
        """
        Adds a mapping associated to a local path to watch.

        @param      key         key in ``http://locahost:8008/key/``
        @param      value       local path

        Python documentation says list are protected against
        multithreading (concurrent accesses).
        If you run the server multiple times, the mappings stays because it
        is a static variable.
        """
        value = os.path.normpath(value)
        if not os.path.exists(value):
            raise FileNotFoundError(value)  # pragma: no cover
        DocumentationHandler.mappings[key] = value

    @staticmethod
    def get_mappings():
        """
        Returns a copy of the mappings.

        @return         dictionary of mappings
        """
        return copy.copy(DocumentationHandler.mappings)

    def __init__(self, request, client_address, server):
        """
        Regular constructor, an instance is created for each request,
        do not store any data for a longer time than a request.
        """
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):
        """
        What to do is case of GET request.
        """
        parsed_path = urlparse(self.path)
        self.serve_content(parsed_path, "GET")

    def do_POST(self):
        """
        What to do is case of POST request.
        """
        parsed_path = urlparse.urlparse(self.path)
        self.serve_content(parsed_path)

    def do_redirect(self, path="/index.html"):
        """
        Redirection when url is just the website.

        @param      path        path to redirect to (a string)
        """
        self.send_response(301)
        self.send_header('Location', path)
        self.end_headers()

    media_types = {
        ".js": ('application/javascript', 'r'),
        ".css": ("text/css", 'r'),
        ".html": ('text/html', 'r'),
        ".py": ('text/html', 'execute'),
        ".png": ('image/png', 'rb'),
        ".jpeg": ('image/jpeg', 'rb'),
        ".jpg": ('image/jpeg', 'rb'),
        ".ico": ('image/x-icon', 'rb'),
        ".gif": ('image/gif', 'rb'),
        ".eot": ('application/vnd.ms-fontobject', 'rb'),
        ".ttf": ('application/font-sfnt', 'rb'),
        ".otf": ('font/opentype', 'rb'),
        ".svg": ('image/svg+xml', 'r'),
        ".woff": ('application/font-wof', 'rb'),
    }

    @staticmethod
    def get_ftype(apath):
        """
        defines the header to send (type of files) based on path
        @param      apath       location (a string)
        @return                 htype, ftype (html, css, ...)

        If a type is missing, you should look for the ``MIME TYPE``
        on a search engine.

        See also `media-types <http://www.iana.org/assignments/media-types/media-types.xhtml>`_
        """
        ext = "." + apath.split(".")[-1]
        htype, ftype = DocumentationHandler.media_types.get(ext, ('', ''))
        return htype, ftype

    def send_headers(self, path):
        """
        defines the header to send (type of files) based on path
        @param      path        location (a string)
        @return                 type (html, css, ...)
        """
        htype, ftype = self.get_ftype(path)

        if htype != '':
            self.send_header('Content-type', htype)
            self.end_headers()
        else:
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
        return ftype

    def get_file_content(self, localpath, ftype, path=None):
        """
        Returns the content of a local file.

        @param      localpath       local filename
        @param      ftype           r or rb
        @param      path            if != None, the filename will be path/localpath
        @return                     content

        This function implements a simple cache mechanism.
        """
        if path is not None:
            tlocalpath = os.path.join(path, localpath)
        else:
            tlocalpath = localpath

        content = DocumentationHandler.get_from_cache(tlocalpath)
        if content is not None:
            self.LOG("serves cached", tlocalpath)
            return content

        if ftype in ("r", "execute"):
            if not os.path.exists(
                    tlocalpath) and "_static/bootswatch" in tlocalpath:
                access = tlocalpath.replace("bootswatch", "bootstrap")
            else:
                access = tlocalpath

            if not os.path.exists(access):
                self.LOG("** w,unable to find: ", access)
                return None

            self.LOG("reading file ", access)
            with open(access, "r", encoding="utf8") as f:
                content = f.read()
                DocumentationHandler.update_cache(tlocalpath, content)
                return content
        else:
            if not os.path.exists(
                    tlocalpath) and "_static/bootswatch" in tlocalpath:
                access = tlocalpath.replace("bootswatch", "bootstrap")
            else:
                access = tlocalpath

            if not os.path.exists(access):
                self.LOG("** w,unable to find: ", access)
                return None

            self.LOG("reading file ", access)
            with open(tlocalpath, "rb") as f:
                content = f.read()
                DocumentationHandler.update_cache(tlocalpath, content)
                return content

    @staticmethod
    def get_from_cache(key):
        """
        Retrieves a file from the cache if it was cached,
        it the file was added later than a day, it returns None.

        @param      key     key
        @return             content or None if None found or too old
        """
        content = DocumentationHandler.cache.get(key, None)
        if content is None:
            return content

        att = DocumentationHandler.cache_attributes[key]
        delta = datetime.datetime.now() - att["date"]
        if delta > DocumentationHandler.cache_refresh:
            del DocumentationHandler.cache[key]
            del DocumentationHandler.cache_attributes[key]
            return None
        else:
            DocumentationHandler.cache_attributes[key]["nb"] += 1
            return content

    @staticmethod
    def update_cache(key, content):
        """
        Updates the cache.

        @param      key         key
        @param      content     content to place
        """
        if len(DocumentationHandler.cache) < 5000:
            # we do not clean here as the cache is shared by every session/user
            # it would not be safe
            # unless we add protection
            # self.clean_cache(1000)
            pass

        # this one first as a document existence is checked by using cache
        DocumentationHandler.cache_attributes[key] = {"nb": 1,
                                                      "date": datetime.datetime.now()}
        DocumentationHandler.cache[key] = content

    @staticmethod
    def _print_cache(n=20):
        """
        Displays the most requested files.
        """
        al = [(v["nb"], k)
              for k, v in DocumentationHandler.cache_attributes.items() if v["nb"] > 1]
        for i, doc in enumerate(sorted(al, reverse=True)):
            if i >= n:
                break
            print("cache: {0} - {1}".format(*doc))

    @staticmethod
    def execute(localpath):
        """
        Locally executes a python script.

        @param      localpath       local python script
        @return                     output, error
        """
        exe = subprocess.Popen([sys.executable, localpath],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, error = exe.communicate()
        return out, error

    def feed(self, anys, script_python=False, params=None):
        """
        Displays something.

        @param      anys                string
        @param      script_python       if True, the function processes script sections
        @param      params              extra parameters when a script must be executed (should be a dictionary)

        A script section looks like:

        ::

            <script type="text/python">
            from pandas import DataFrame
            pars = [ { "key":k, "value":v } for k,v in params ]
            tbl = DataFrame (pars)
            print ( tbl.to_html(class_table="myclasstable") )
            </script>

        The server does not interpret Python, to do that, you need to use
        `pyrsslocal <http://www.xavierdupre.fr/app/pyrsslocal/helpsphinx/index.html>`_.
        """
        if isinstance(anys, bytes):
            if script_python:
                raise SystemError(  # pragma: no cover
                    "** w,unable to execute script from bytes")
            self.wfile.write(anys)
        else:
            if script_python:
                #any = self.process_scripts(any, params)
                raise NotImplementedError(  # pragma: no cover
                    "unable to execute a python script")
            text = anys.encode("utf-8")
            self.wfile.write(text)

    def shutdown(self):
        """
        Shuts down the service.
        """
        raise NotImplementedError()  # pragma: no cover

    def serve_content(self, cpath, method="GET"):
        """
        Tells what to do based on the path. The function intercepts the
        path /localfile/, otherwise it calls ``serve_content_web``.

        If you type ``http://localhost:8080/root/file``,
        assuming ``root`` is mapped to a local folder.
        It will display this file.

        @param      cpath        ParseResult
        @param      method      GET or POST
        """
        if cpath.path == "" or cpath.path == "/":
            params = parse_qs(cpath.query)
            self.serve_main_page()
        else:
            params = parse_qs(cpath.query)
            params["__path__"] = cpath

            # fullurl = cpath.geturl()
            fullfile = cpath.path
            params["__url__"] = cpath
            spl = fullfile.strip("/").split("/")

            project = spl[0]
            link = "/".join(spl[1:])
            value = DocumentationHandler.mappings.get(project, None)

            if value is None:
                self.LOG("can't serve", cpath)
                self.LOG("with params", params)
                self.send_response(404)
                #raise KeyError("unable to find a mapping associated to: " + project + "\nURL:\n" + url + "\nPARAMS:\n" + str(params))

            elif value == "shut://":
                self.LOG("call shutdown")
                self.shutdown()

            elif value == "http://":
                self.send_response(200)
                self.send_headers("debug.html")
                url = cpath.path.replace("/%s/" % project, "")
                try:
                    content = get_url_content(url)
                except Exception as e:  # pragma: no cover
                    content = "<html><body>ERROR (2): %s</body></html>" % e
                self.feed(content, False, params={})

            else:
                if ".." in link:
                    # we avoid that case to prevent users from digging others paths
                    # than the mapped ones, just in that the browser does not
                    # remove them
                    self.send_error(404)
                    self.feed("Requested resource %s unavailable" % link)
                else:
                    # we do not expect the documentation to point to the root
                    # it must be relative paths
                    localpath = link.lstrip("/")
                    if localpath in [None, "/", ""]:
                        localpath = "index.html"
                    fullpath = os.path.join(value, localpath)
                    self.LOG("localpath ", fullpath, os.path.isfile(fullpath))

                    self.send_response(200)
                    _, ftype = self.get_ftype(localpath)

                    execute = eval(params.get("execute", ["True"])[0])
                    spath = params.get("path", [None])[0]
                    # keep = eval(params.get("keep", ["False"])[0])

                    if ftype != 'execute' or not execute:
                        content = self.get_file_content(fullpath, ftype, spath)
                        if content is None:
                            self.LOG("** w,unable to get file for key:", spath)
                            self.send_error(404)
                            self.feed(
                                "Requested resource %s unavailable" % localpath)
                        else:
                            ext = os.path.splitext(localpath)[-1].lower()
                            if ext in [
                                    ".py", ".c", ".cpp", ".hpp", ".h", ".r", ".sql", ".java"]:
                                self.send_headers(".html")
                                self.feed(
                                    DocumentationHandler.html_code_renderer(localpath, content))
                            elif ext in [".html"]:
                                content = DocumentationHandler.process_html_path(
                                    project, content)
                                self.send_headers(localpath)
                                self.feed(content)
                            else:
                                self.send_headers(localpath)
                                self.feed(content)
                    else:
                        self.LOG("execute file ", localpath)
                        out, err = DocumentationHandler.execute(localpath)
                        if len(err) > 0:
                            self.send_error(404)
                            self.feed(
                                "Requested resource %s unavailable" % localpath)
                        else:
                            self.send_headers(localpath)
                            self.feed(out)

    @staticmethod
    def process_html_path(project, content):
        """
        Processes a :epkg:`HTML` content, replaces path which are relative
        to the root and not the project.

        @param      project     project, ex: ``pyquickhelper``
        @param      content     page content
        @return                 modified content
        """
        #content = content.replace(' src="',' src="' + project + '/')
        #content = content.replace(' href="',' href="' + project + '/')
        return content

    @staticmethod
    def html_code_renderer(localpath, content):
        """
        Produces a html code for code.

        @param      localpath   local path to file (local or not)
        @param      content     content of the file
        @return                 html string
        """
        res = [DocumentationHandler.html_header % (localpath)]
        res.append("<pre class=\"prettyprint\">")
        res.append(content.replace("<", "&lt;").replace(">", "&gt;"))
        res.append(DocumentationHandler.html_footer)
        return "\n".join(res)

    def serve_content_web(self, path, method, params):
        """
        Functions to overload (executed after serve_content).

        @param      path        ParseResult
        @param      method      GET or POST
        @param      params      params parsed from the url + others
        """
        self.send_response(200)
        self.send_headers("")
        self.feed("** w,unable to serve content for url: " +
                  path.geturl() + "\n" + str(params) + "\n")
        self.send_error(404)

    def serve_main_page(self):  # pragma: no cover
        """
        Displays all the mapping for the default path.
        """
        rows = ["<html><body>"]
        rows.append("<h1>Documentation Server</h1>")
        rows.append("<ul>")
        for k, _ in sorted(DocumentationHandler.mappings.items()):
            if not k.startswith("_"):
                row = '<li><a href="{0}/">{0}</a></li>'.format(k)
                rows.append(row)
        rows.append("</ul></body></html>")
        content = "\n".join(rows)

        self.send_response(200)
        self.send_headers(".html")
        self.feed(content)


class DocumentationThreadServer (Thread):

    """
    defines a thread which holds a web server

    @var    server      the server of run
    """

    def __init__(self, server):
        """
        @param      server to run
        """
        Thread.__init__(self)
        self.server = server

    def run(self):
        """
        Runs the server.
        """
        self.server.serve_forever()

    def shutdown(self):
        """
        Shuts down the server, if it does not work, you can still kill
        the thread:

        ::

            self.kill()
        """
        self.server.shutdown()
        self.server.server_close()


def run_doc_server(server, mappings, thread=False, port=8079):
    """
    Runs the server.

    @param      server      if None, it becomes ``HTTPServer(('localhost', 8080), DocumentationHandler)``
    @param      mappings    prefixes with local folders (dictionary)
    @param      thread      if True, the server is run in a thread
                            and the function returns right away,
                            otherwise, it runs the server.
    @param      port        port to use
    @return                 server if thread is False, the thread otherwise (the thread is started)

    .. faqref::
        :title: How to run a local server which serves the documentation?

        The following code will create a local server: `http://localhost:8079/pyquickhelper/ <http://localhost:8079/pyquickhelper/>`_.

        ::

            this_fold = os.path.dirname(pyquickhelper.serverdoc.documentation_server.__file__)
            this_path = os.path.abspath( os.path.join( this_fold,
                        "..", "..", "..", "dist", "html") )
            run_doc_server(None, mappings = { "pyquickhelper": this_path } )

        The same server can serves more than one project.
        More than one mappings can be sent.
    """
    for k, v in mappings.items():
        DocumentationHandler.add_mapping(k, v)

    if server is None:
        server = HTTPServer(('localhost', port), DocumentationHandler)
    elif isinstance(server, str):
        server = HTTPServer((server, port), DocumentationHandler)
    elif not isinstance(server, HTTPServer):
        raise TypeError(  # pragma: no cover
            "unexpected type for server: " + str(type(server)))

    if thread:
        th = DocumentationThreadServer(server)
        th.start()
        return th
    else:  # pragma: no cover
        server.serve_forever()
        return server


if __name__ == '__main__':  # pragma: no cover

    run_server = True
    if run_server:
        # http://localhost:8079/pyquickhelper/
        this_fold = os.path.abspath(os.path.dirname(__file__))
        this_fold2 = os.path.join(
            this_fold, "..", "..", "..", "..", "ensae_teaching_cs", "dist", "html3")
        this_fold = os.path.join(this_fold, "..", "..", "..", "dist", "html")
        fLOG(OutputPrint=True)
        fLOG("running server")
        run_doc_server(None, mappings={"pyquickhelper": this_fold,
                                       "ensae_teaching_cs": this_fold2})
        fLOG("end running server")
