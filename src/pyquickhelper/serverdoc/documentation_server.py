#-*- coding:utf-8 -*-
"""
@file
@brief This file defines a simple local server delivering generating documentation.
"""

"""
@file
@brief  This modules contains a class which implements a simple server.
"""

import sys, string, cgi, time, os, subprocess, socket, copy, re, io, datetime
from urllib.parse import urlparse, parse_qs
from io import StringIO
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler

if __name__ == "__main__" :
    path = os.path.normpath(os.path.abspath(os.path.join(os.path.split(__file__)[0],"..","..","..", "src")))
    if path not in sys.path : sys.path.append(path)
    path = os.path.normpath(os.path.abspath(os.path.join(os.path.split(__file__)[0],"..","..","..", "..","pyquickhelper","src")))
    if path not in sys.path : sys.path.append(path)
    from pyquickhelper import fLOG
else :
    from ..loghelper.flog import fLOG


class DocumentationHandler(BaseHTTPRequestHandler):
    """
    Define a simple handler used by HTTPServer,
    it just serves local content.
    
    """
    
    mappings = {    "__fetchurl__": "http://",
                    "__shutdown__": "shut://",
                }
    
    html_header = """
            <?xml version="1.0" encoding="utf-8"?>
            <html>
            <head>
            <title>%s</title>
            </head>
            <body>
            """.replace("            ","")

    html_footer = """
            </body>
            </html>
            """.replace("            ","")
            
    cache = { }
    cache_attributes = { }
    cache_refresh = datetime.timedelta(1)
            
    def LOG(self, *l, **p):
        """
        logging function
        """
        fLOG(*l, **p)

    @staticmethod
    def add_mapping(key, value) :
        """
        adds a mapping associated to a local path to watch
        @param      key         key in ``http://locahost:8008/key/
        @param      value       local path
        
        Python documentation says list are proctected against multithreads (concurrent accesses).
        
        If you run the server multitimes, the mappings stays because it 
        is a static variable.
        """
        value = os.path.normpath(value)
        if not os.path.exists(value):
            raise FileNotFoundError(value)
        DocumentationHandler.mappings[key] = value
        
    @staticmethod    
    def get_mappings():
        """
        returns a copy of the mappings
        
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
        what to do is case of GET request
        """
        parsed_path = urlparse(self.path)
        self.serve_content(parsed_path, "GET")
        
    def do_POST(self):
        """
        what to do is case of POST request
        """
        parsed_path = urlparse.urlparse(self.path)
        self.serve_content(parsed_path)
        
    def do_redirect(self, path="/index.html"):
        """
        redirection when url is just the website
        @param      path        path to redirect to (a string)
        """
        self.send_response(301)
        self.send_header('Location', path)
        self.end_headers()
        
    media_types = {
            ".js"   : ( 'application/javascript', 'r' ),
            ".css"  : ("text/css", 'r'),
            ".html" : ('text/html', 'r'),
            ".py"   : ('text/html','execute'),
            ".png"  : ('image/png','rb'),
            ".jpg"  : ('image/jpeg','rb'),
            ".ico"  : ('image/x-icon','rb'),
            ".gif"  : ('image/gif','rb'),
            ".eot"  : ('application/vnd.ms-fontobject','rb'),
            ".ttf"  : ('application/font-sfnt','rb'),
            ".otf"  : ('font/opentype','rb'),
            ".svg"  : ('image/svg+xml','r'),
            ".woff" : ('application/font-wof','rb'),
           }
        
    def get_ftype(self, path):
        """
        defines the header to send (type of files) based on path
        @param      path        location (a string)
        @return                 htype, ftype (html, css, ...)
        
        If a type is missing, you should look for the ``MIME TYPE``
        on a search engine.
        
        See also `media-types <http://www.iana.org/assignments/media-types/media-types.xhtml>`_ 
        """
        ext = "." + path.split(".")[-1]
        htype, ftype = DocumentationHandler.media_types.get(ext, ('',''))
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
        
    def get_file_content(self, localpath, ftype, path = None):
        """
        Returns the content of a local file. The function also looks into
        folders in ``self.__pathes`` to see if the file can be found in one of the 
        folder when not found in the first one.
        
        @param      localpath       local filename
        @param      ftype           r or rb
        @param      path            if != None, the filename will be path/localpath
        @return                     content
        
        This function implements a simple cache mechanism.
        """
        if path is not None :
            tlocalpath = os.path.join(path, localpath)
        else : 
            tlocalpath = localpath
            
        content = self.get_from_cache(tlocalpath)
        if content is not None : 
            self.LOG("serves cached",tlocalpath)
            return content
            
        if not os.path.exists(tlocalpath) :
            self.send_error(404)
            content = "unable to find file " + localpath
            self.LOG(content)
            return content
            
        if ftype == "r" or ftype == "execute" :
            self.LOG("reading file ", tlocalpath)
            with open(tlocalpath, "r", encoding="utf8") as f :
                content = f.read()
                self.update_cache(tlocalpath, content)
                return content
        else :
            self.LOG("reading file ", tlocalpath)
            with open(tlocalpath, "rb") as f :
                content = f.read()
                self.update_cache(tlocalpath, content)
                return content
                
    def get_from_cache(self, key):
        """
        retrieve a file from the cache if it was cached, 
        it the file was added later than a day, it returns None
        
        @param      key     key
        @return             content or None if None found or too old
        """
        content = DocumentationHandler.cache.get(key, None)
        if content is None : 
            return content
            
        att = DocumentationHandler.cache_attributes [ key ]
        delta = datetime.datetime.now() - att["date"]
        if delta > DocumentationHandler.cache_refresh:
            del DocumentationHandler.cache[key]
            del DocumentationHandler.cache_attributes[key]
            return None
        else:
            DocumentationHandler.cache_attributes[key]["nb"] += 1
            return content
            
    def update_cache(self, key, content):
        """
        update the cache
        
        @param      key         key
        @param      content     content to place
        """
        if len(DocumentationHandler.cache) < 5000 :
            # we do not clean here as the cache is shared by every session/user
            # it would not be safe
            # unless we add protection
            #self.clean_cache(1000)
            pass
            
        # this one first as a document existence is checked by using cache
        DocumentationHandler.cache_attributes[key] = {"nb":1,
                    "date": datetime.datetime.now() }
        DocumentationHandler.cache[key] = content
        
    def _print_cache(self, n = 20):
        """
        display the most requested files
        """
        al = [ (v["nb"], k) for k,v in DocumentationHandler.cache_attributes.items() if v["nb"] > 1 ]
        for i,doc in enumerate(sorted(al,reverse=True)):
            if i >= n: break
            print("cache: {0} - {1}".format(*doc))

    def execute(self, localpath):
        """
        locally execute a python script
        @param      localpath       local python script
        @return                     output, error
        """
        exe = subprocess.Popen([sys.executable, localpath], 
                               stdout = subprocess.PIPE, 
                               stderr = subprocess.PIPE)
        out, error = exe.communicate()
        return out, error
        
    def feed(self, any, script_python = False, params = { }):
        """
        displays something
        
        @param      any                 string
        @param      script_python       if True, the function processes script sections
        @param      params              
        
        A script section looks like:
        @code
        <script type="text/python">
        from pandas import DataFrame
        pars = [ { "key":k, "value":v } for k,v in params ]
        tbl = DataFrame (pars)
        print ( tbl.tohtml(class_table="myclasstable") )
        </script>
        @endcode
        
        The server does not interpret Python, to do that, you need to use
        `pyrsslocal <http://www.xavierdupre.fr/app/pyrsslocal/helpsphinx/index.html>`_.
        """
        if isinstance (any, bytes) :
            if script_python : 
                raise SystemError("unable to execute script from bytes")
            self.wfile.write(any)
        else :
            if script_python :
                any = self.process_scripts(any, params)
            text = any.encode("utf-8")
            self.wfile.write(text)
        
    def shutdown(self):
        """
        Shuts down the service from the service itself (not from another thread). 
        For the time being, the function generates the following exception:
        @code
        Traceback (most recent call last):
          File "simple_server_custom.py", line 225, in <module>
            run_server(None)
          File "simple_server_custom.py", line 219, in run_server
            server.serve_forever()
          File "c:\python33\lib\socketserver.py", line 237, in serve_forever
            poll_interval)
          File "c:\python33\lib\socketserver.py", line 155, in _eintr_retry
            return func(*args)
        ValueError: file descriptor cannot be a negative integer (-1)
        @endcode
        
        A better way to shut it down should is recommended. The use of the function:
        @code
        self.server.shutdown()
        @endcode
        freezes the server because this function should not be run in the same thread.
        """
        self.server.socket.close()
        self.LOG("end of shut down")
        
    def serve_content(self, path, method = "GET"):
        """
        Tells what to do based on the path. The function intercepts the 
        path /localfile/, otherwise it calls ``serve_content_web``.
        
        If you type ``http://localhost:8080/root/file``, 
        assuming ``root`` is mapped to a local folder.
        It will display this file.
        
        @param      path        ParseResult
        @param      method      GET or POST
        """
        if path.path == "" or path.path == "/":
            params = parse_qs(path.query)
            self.serve_main_page()
        else:
            params = parse_qs(path.query)
            params["__path__"] = path
            
            fullurl = path.geturl()
            fullfile = path.path
            params["__url__"] = path
            spl = fullfile.strip("/").split("/")
            
            project = spl[0]
            link = "/".join(spl[1:])
            value = DocumentationHandler.mappings.get(project, None)
            
            if value is None:
                self.LOG("can't serve",path)
                self.LOG("with params",params)
                return
                #raise KeyError("unable to find a mapping associated to: " + project + "\nURL:\n" + url + "\nPARAMS:\n" + str(params))
            
            if value == "shut://":
                self.LOG("call shutdown")
                self.shutdown()  
                
            elif value == "http://":
                self.send_response(200)
                self.send_headers("debug.html")
                url = path.path.replace ("/%s/"%project, "")
                try :
                    content = get_url_content_timeout(url)
                except Exception as e :
                    content = "<html><body>ERROR (2): %s</body></html>" % e
                self.feed(content, False, params = { })
            
            else:
                localpath = link
                if localpath in [None, "/", ""] :
                    localpath = "index.html"
                fullpath  = os.path.join( value, localpath )
                self.LOG("localpath ", fullpath, os.path.isfile(fullpath))
                
                self.send_response(200)
                _,ftype   = self.get_ftype(localpath)
                
                execute = eval(params.get("execute",["True"])[0])
                path    = params.get("path",[None])[0]
                keep    = eval(params.get("keep",["False"])[0])
                
                if keep and path not in self.get_pathes():
                    self.LOG("execute", execute , "- ftype", ftype, " - path", path, " keep ", keep)
                    self.add_path(path)
                else :
                    self.LOG("execute", execute , "- ftype", ftype, " - path", path)

                if ftype != 'execute' or not execute :
                    content = self.get_file_content(fullpath, ftype, path)
                    ext = os.path.splitext(localpath)[-1].lower()
                    if ext in [".py", ".c", ".cpp", ".hpp", ".h", ".r", ".sql", ".java"] :
                        self.send_headers (".html")
                        self.feed ( self.html_code_renderer (localpath, content) )
                    elif ext in [".html"]:
                        content = self.process_html_path(project, content)
                        self.send_headers (localpath)
                        self.feed(content)
                    else:
                        self.send_headers (localpath)
                        self.feed(content)
                else:
                    self.LOG("execute file ", localpath)
                    out,err = self.execute (localpath)
                    if len(err) > 0 :
                        self.send_error(404)
                        self.feed("Requested resource %s unavailable" % localpath )
                    else :
                        self.send_headers (localpath)
                        self.feed(out)
                        
    def process_html_path(self, project, content):
        """
        process a HTML content, replace path which are relative
        to the root and not the project
        
        @param      project     project, ex: ``pyquickhelper``
        @param      content     page content 
        @return                 modified content
        """
        #content = content.replace(' src="',' src="' + project + '/')
        #content = content.replace(' href="',' href="' + project + '/')
        return content
                                            
    def html_code_renderer(self, localpath, content):
        """
        produces a html code for code
        
        @param      localpath   local path to file (local or not)
        @param      content     content of the file
        @return                 html string
        """
        res = [ DocumentationHandler.html_header % (localpath) ]
        res.append ("<pre class=\"prettyprint\">")
        res.append(content.replace("<","&lt;").replace(">","&gt;"))
        res.append(DocumentationHandler.html_footer)
        return "\n".join(res)
                
    def serve_content_web(self, path, method, params):
        """
        functions to overload (executed after serve_content)
        
        @param      path        ParseResult
        @param      method      GET or POST
        @param      params      params parsed from the url + others
        """
        self.send_response(200)
        self.send_headers("")
        self.feed("unable to serve content for url: " + path.geturl() + "\n" + str(params) + "\n")
        self.send_error(404)
        
    def serve_main_page(self):
        """
        displays all the mapping for the default path
        """
        rows = ["<html><body>"]
        rows.append("<h1>Documentation Server</h1>")
        rows.append("<ul>")
        for k,v in sorted(DocumentationHandler.mappings.items()):
            if not k.startswith("_"):
                row = '<li><a href="{0}/">{0}</a></li>'.format(k)
                rows.append(row)
        rows.append("</ul></body></html>")
        content = "\n".join(rows)
        
        self.send_response(200)
        self.send_headers (".html")
        self.feed(content)
        
                
class DocumentationThreadServer (Thread) :
    """
    defines a thread which holds a web server
    
    @var    server      the server of run
    """
    
    def __init__ (self, server) :
        """
        constructor
        @param      server to run
        """
        Thread.__init__(self)
        self.server = server
        
    def run(self):
        """
        run the server
        """
        self.server.serve_forever()
        
    def shutdown(self):
        """
        shuts down the server, if it does not work, you can still kill
        the thread: 
        @code
        self.kill()
        @endcode
        """
        self.server.shutdown()
        
        
def run_doc_server (server, 
                mappings,
                thread = False, 
                port = 8079) :
    """
    run the server
    @param      server      if None, it becomes ``HTTPServer(('localhost', 8080), DocumentationHandler)``
    @param      mappings    mapping: prefixes with local folders
    @param      thread      if True, the server is run in a thread
                            and the function returns right away,
                            otherwite, it runs the server.
    @param      port        port to use
    @return                 server if thread is False, the thread otherwise (the thread is started)
    
    @example(run a local server which serves the documentation)
    
    The following code will create a local server: `http://localhost:8079/pyquickhelper/ <http://localhost:8079/pyquickhelper/>`_.
    @code
    this_fold = os.path.dirname(pyquickhelper.serverdoc.documentation_server.__file__)
    this_path = os.path.abspath( os.path.join( this_fold, "..", "..", "..", "dist", "html") )
    run_doc_server(None, mappings = { "pyquickhelper": this_path } )
    @endcode
    
    The same server can serves more than one projet. 
    More than one mappings can be sent.
    @endexample
    
    """
    for k,v in mappings.items():
        DocumentationHandler.add_mapping(k,v)
        
    if server == None : 
        server = HTTPServer(('localhost', port), DocumentationHandler)
    elif isinstance(server, str):
        server = HTTPServer((server, port), DocumentationHandler)
    elif not isinstance(server, HTTPServer):
        raise TypeError("unexpected type for server: " + str(type(server)))
        
    if thread :
        th = DocumentationThreadServer(server)
        th.start()
        return th
    else :
        server.serve_forever()
        return server

if __name__ == '__main__':
    
    
    if True:
        # http://localhost:8079/pyquickhelper/
        this_fold  = os.path.abspath(os.path.dirname(__file__))
        this_fold2 = os.path.join(this_fold, "..", "..", "..", "..", "ensae_teaching_cs", "dist", "html3")
        this_fold  = os.path.join(this_fold, "..", "..", "..", "dist", "html")
        fLOG(OutputPrint=True)
        fLOG("running server")
        run_doc_server(None, mappings = {   "pyquickhelper": this_fold,   
                                            "ensae_teaching_cs": this_fold2 } )
        fLOG("end running server")
    
