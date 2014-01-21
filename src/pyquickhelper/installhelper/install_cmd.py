# coding: latin-1
"""
@file
@brief Various function to install various python module from various location.
"""
import sys, re, platform, webbrowser, os, urllib, urllib.request, imp, zipfile,time, subprocess, io
fLOG = print

def python_version():
    """
    retrieve the platform and version of this python
    
    @return     tuple, example: ("win32","32bit") or ("win32","64bit")
    """
    return sys.platform, platform.architecture()[0]
    
def run_cmd (   cmd, 
                sin             = "", 
                shell           = False, 
                wait            = False, 
                log_error       = True,
                secure          = None,
                stop_waiting_if = None,
                do_not_log      = False,
                encerror        = "ignore",
                encoding        = "utf8") :
    """
    run a command line and wait for the result
    @param      cmd                 command line
    @param      sin                 sin: what must be written on the standard input
    @param      shell               if True: cmd is a shell command (and no command window is opened)
    @param      wait                call proc.wait
    @param      log_error           if log_error, call fLOG (error)
    @param      secure              if secure is a string (a valid filename), the function stores the output in a file
                                    and reads it continuously
    @param      stop_waiting_if     the function stops waiting if some condition is fulfilled.
                                    The function received the last line from the logs.
    @param      do_not_log          do not log the output
    @param      encerror            encoding errors (ignore by default) while converting the output into a string
    @param      encoding            encoding of the output
    @return                         content of stdout, stdres  (only if wait is True)  
    """
    if secure != None :
        fLOG("secure=",secure)
        with open(secure,"w") as f : f.write("")
        add = ">%s" % secure 
        if isinstance (cmd, str) : cmd += " " + add
        else : cmd.append(add)
    if not do_not_log : 
        fLOG ("execute ", cmd)
    
    if sys.platform.startswith("win") :
        
        startupinfo = subprocess.STARTUPINFO()    
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        proc = subprocess.Popen (cmd, 
                                 shell = shell, 
                                 stdout = subprocess.PIPE, 
                                 stderr = subprocess.PIPE,
                                 startupinfo = startupinfo)
    else :
        proc = subprocess.Popen (split_cmp_command(cmd),
                                 shell = shell, 
                                 stdout = subprocess.PIPE, 
                                 stderr = subprocess.PIPE)
    if wait : 
    
        out = [ ]
        skip_waiting = False
        
        if secure == None :
            for line in proc.stdout :
                if not do_not_log : 
                    fLOG(line.decode(encoding, errors=encerror))
                try :
                    out.append(line.decode(encoding, errors=encerror))
                except UnicodeDecodeError as exu :
                    raise Exception("issue with cmd:" + str(cmd) + "\n" + str(exu))
                if proc.stdout.closed: 
                    break
                if stop_waiting_if != None and stop_waiting_if(line.decode("utf8", errors=encerror)) :
                    skip_waiting = True
                    break
        else :
            last = []
            while proc.poll() == None :
                if os.path.exists (secure) :
                    with open(secure,"r") as f :
                        lines = f.readlines()
                    if len(lines) > len(last) :
                        for line in lines[len(last):] :
                            if do_not_log : 
                                fLOG(line)
                            out.append(line)
                        last = lines
                    if stop_waiting_if != None and len(last)>0 and stop_waiting_if(last[-1]) :
                        skip_waiting = True
                        break
                time.sleep(0.1)
         
        if do_not_log : 
            fLOG("end waiting 0")
        if not skip_waiting :
            proc.wait ()
        
        if do_not_log : 
            fLOG("end waiting")
        out = "\n".join(out)
        err = proc.stderr.read().decode(encoding, errors=encerror)
        if not do_not_log : 
            fLOG ("end of execution ", cmd)
        if len (err) > 0 and log_error :
            fLOG ("error (log)\n%s" % err)
        #return bytes.decode (out, errors="ignore"), bytes.decode(err, errors="ignore")
        return out, err
    else :
        return "",""    

class ModuleInstall :
    """
    defines the necessary information for a module
    """
    
    allowedKind = ["pip", "github", "exe"]
    expKPage = "onclick=.javascript:dl[(]([,\\[\\]0-9]+) *, *.([0-9&;@?=:A-Zgtl]+).[)]. title(.+)?.>(.+?win32-py3.3.exe)</a>"
    exeLocation = "http://www.lfd.uci.edu/~gohlke/pythonlibs/"
    gitexe = r"C:\Program Files (x86)\Git"
    
    def __init__(self, name, kind = "pip", gitrepo = None, mname = None):
        """
        constructor
        
        @param      name            name
        @param      kind            kind of installation (pip, github, exe)
        @param      gitrepo         github repository (example: sdpython)
        @param      mname           sometimes, the module name is different from its official name
        
        exe is only for Windows.
        """
        self.name = name
        self.kind = kind
        self.gitrepo = gitrepo
        self.mname = mname
        if self.kind not in ModuleInstall.allowedKind:
            raise Exception("unable to interpret kind {0}, it should be in {1}".format(kind, ",".join(ModuleInstall.allowedKind)))
        if self.kind == "github" and self.gitrepo == None :
            raise Exception("gitrepo cannot be empty")
            
    def __str__(self):
        """
        usual
        """
        return "{0}:{1}:import {2}".format(self.name,self.kind, self.ImportName)
    
    @property
    def ImportName(self):
        """
        return the import name
        """
        if self.mname != None : return self.mname
        if self.name.startswith("python-"): return self.name[len("python-"):]
        else: return self.name
        
    def IsInstalled(self):
        """
        checks if a module is installed
        """
        try :
            r = imp.find_module(self.ImportName)
            return True
        except ImportError :
            return False
        
    def get_exe_url_link(self) :
        """
        for windows, get the url of the setup using a webpage
        
        @return     url, exe name
        """
        version = python_version()
        plat    = version[0] if version[0] == "win32" else version[1]
        pattern = ModuleInstall.expKPage.replace("win32-py3.3.exe","{0}-py{1}.{2}.exe".format(plat,sys.version_info.major,sys.version_info.minor))
        expre   = re.compile(pattern)
        
        if "cached_page" not in self.__dict__ :
            page = os.path.join(os.path.split(__file__)[0],"page.html")
            if os.path.exists(page) :
                with open(page,"r",encoding="utf8") as f : text = f.read()
            else :
                req = urllib.request.Request(ModuleInstall.exeLocation, headers= { 'User-agent': 'Mozilla/5.0' })
                u = urllib.request.urlopen(req)
                text = u.read()
                u.close()
                text = text.decode("utf8")
                
            text = text.replace("&quot;","'")
            self.cached_page = text
            
        page = self.cached_page
        all  = expre.findall(page)
        if len(all) == 0 :
            raise Exception("unable to find regex with pattern: " + pattern)

        all = [ _ for _ in all if _[-1].startswith(self.name + "-") ]
        if len(all) == 0 :
            raise Exception("unable to find a single link for " + self.name)
        link = all[-1]
        
        def dc(ml,mi):
                ot=""
                for j in range(0,len(mi)) :
                    ot+= chr(ml[ord(mi[j])-48])
                return ot
        def dl1(ml,mi):
            ot=""
            for j in range(0,len(mi)):
                ot+=chr(ml[ord(mi[j])-48])
            return ot
        def dl(ml,mi):
            mi=mi.replace('&lt;','<')
            mi=mi.replace('&gt;','>')
            mi=mi.replace('&amp;','&')
            return dl1(ml,mi)
        
        url = dl(eval(link[0]),link[1])
        return ModuleInstall.exeLocation + url, link[-1]
        
    def unzipfiles(self, zipf, whereTo):
        """
        unzip files from a zip archive
        
        @param      zipf        archive
        @param      whereTo     destinatation folder
        @return                 list of unzipped files
        """
        file = zipfile.ZipFile (zipf, "r")
        files = []
        for info in file.infolist () :
            if not os.path.exists (info.filename) :
                data = file.read (info.filename)
                tos = os.path.join (whereTo, info.filename)
                if not os.path.exists (tos) :
                    finalfolder = os.path.split(tos)[0]
                    if not os.path.exists (finalfolder) :
                        fLOG ("    creating folder ", finalfolder)
                        os.makedirs (finalfolder)
                    if not info.filename.endswith ("/") :
                        u = open (tos, "wb")
                        u.write ( data )
                        u.close()
                        files.append (tos)
                        fLOG ("    unzipped ", info.filename, " to ", tos)
                elif not tos.endswith("/") :
                    files.append (tos)
            elif not info.filename.endswith ("/") :
                files.append (info.filename)
        return files
        
    def install(self, force_kind = None, force = False, temp_folder = "."):
        """
        install the package
        
        @param      force_kind      overwrite self.kind
        @param      force           force the installation even if already installed
        @param      temp_folder     folder where to download the setup
        @return                     boolean
        """
        
        if not force and self.IsInstalled() :
            return True
            
        fLOG("installation of ", self)        
        kind = force_kind if force_kind != None else self.kind
        
        if kind == "pip" :
            pip = os.path.join(os.path.split(sys.executable)[0],"Scripts","pip.exe")
            cmd = pip + " install {0}".format(self.name)
            out, err = run_cmd(cmd, wait = True, do_not_log = True)
            if "Successfully installed" not in out :
                raise Exception("unable to install " + str(self) + "\n" + out + "\n" + err)
            return True
            
        elif kind == "github" :
            # the following code requires admin rights
            #if python_version()[0].startswith("win") and kind == "git" and not os.path.exists(ModuleInstall.gitexe) :
            #    raise FileNotFoundError("you need to install github first: see http://windows.github.com/")
            #if python_version()[0].startswith("win"):
            #    os.chdir(os.path.join(ModuleInstall.gitexe,"bin"))
            #cmd = pip + " install -e git://github.com/{0}/{1}-python.git#egg={1}".format(self.gitrepo, self.name)
            
            outfile = os.path.join(temp_folder, self.name + ".zip")
            if force or not os.path.exists(outfile) :
                zipurl = "https://github.com/sdpython/{0}/archive/master.zip".format(self.name)
                fLOG("downloading", zipurl)
                req = urllib.request.Request(zipurl, headers= { 'User-agent': 'Mozilla/5.0' })
                u = urllib.request.urlopen(req)
                text = u.read()
                u.close()
            
                if not os.path.exists(temp_folder) : 
                    os.makedirs(temp_folder)
                u = open (outfile, "wb")
                u.write ( text )
                u.close()            
            
            fLOG("unzipping ", outfile)
            files = self.unzipfiles(outfile, temp_folder)
            setu = [ _ for _ in files if _.endswith("setup.py") ]
            if len(setu) != 1 :
                raise Exception("unable to find setup.py for module " + self.name)
            setu = os.path.abspath(setu[0])
            
            fLOG("install ", outfile)
            cwd = os.getcwd()
            os.chdir(os.path.split(setu)[0])
            cmd = "{0} setup.py install".format(sys.executable.replace("pythonw.ewe","python.exe"))
            out, err = run_cmd(cmd, wait = True, do_not_log = True)
            os.chdir(cwd)
            if "Successfully installed" not in out :
                raise Exception("unable to install " + str(self) + "\n" + out + "\n" + err)
            return "Successfully installed" in out
            
        elif kind == "exe":
            ver = python_version()
            if ver[0] != "win32":
                return self.install("pip")
            else :
                url,exe = self.get_exe_url_link()

                fLOG("downloading", exe)
                req = urllib.request.Request(url, headers= { 'User-agent': 'Mozilla/5.0' })
                u = urllib.request.urlopen(req)
                text = u.read()
                u.close()
                
                if not os.path.exists(temp_folder) : 
                    os.makedirs(temp_folder)
                
                exename = os.path.join(temp_folder,exe)
                fLOG("writing", exe)
                with open(exename,"wb") as f : f.write(text)
                
                fLOG("executing", exe)
                out,err = run_cmd(exename, wait=True, do_not_log = True)
                return len(err) == 0
                
                
def complete_installation():
    """
    returns a list of module to install to get 
    """
    return [   
                ModuleInstall("setuptools", "exe"),
                ModuleInstall("pip", "exe"),
                ModuleInstall("numpy", "exe"),
                ModuleInstall("scipy", "exe"),
                ModuleInstall("matplotlib", "exe"),
                ModuleInstall("lxml", "exe"),
                ModuleInstall("scipy", "exe"),
                ModuleInstall("selenium", "pip"),
                #ModuleInstall("pyquickhelper", "github", "sdpython"),
                #ModuleInstall("pyensae", "github", "sdpython"),
                #ModuleInstall("pyrsslocal", "github", "sdpython"),
                ModuleInstall("python-pptx", "github", "sdpython"),
                ModuleInstall("python-nvd3", "github", "sdpython"),
                ModuleInstall("d3py", "github", "sdpython"),
                ModuleInstall("splinter", "github", "cobrateam"),
                ModuleInstall("sphinx", "pip"),
                ModuleInstall("jinja2", "pip"),
                ModuleInstall("rpy2", "exe"),
                ModuleInstall("pywin32", "exe", mname = "win32api" ),
                ModuleInstall("ipython", "exe"),
                ModuleInstall("pandas", "exe"),
                ModuleInstall("Pillow", "exe", mname = "PIL"),
                ModuleInstall("pygments", "pip"),
                ModuleInstall("pyparsing", "pip"),
                ModuleInstall("networkx", "exe"),
                #ModuleInstall("cvxopt", "exe"),
                ModuleInstall("coverage", "pip"),
                ModuleInstall("pyreadline", "pip"),
                ModuleInstall("scikit-learn", "exe", mname="sklearn"),
                #ModuleInstall("PyQt", "exe", mname="pyqt"),
                ModuleInstall("pygame", "exe"),
                #ModuleInstall("pythonnet", "exe"),
            ]
                

if __name__ == "__main__" :
    for _ in complete_installation() :
        _.install(temp_folder="install")
    