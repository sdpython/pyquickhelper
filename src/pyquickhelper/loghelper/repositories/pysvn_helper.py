"""
@file
@brief  Gather all pysvn functionalities here. There might be some differences
between SVN version, pysvn client version, TortoiseSVN version and Python.
If such a case happens, most of the function will call ``svn`` using the command line.
"""

import os,sys,datetime
import xml.etree.ElementTree as ET

from ..flog import fLOG, run_cmd
from ..convert_helper import str_to_datetime

def IsRepo(location, commandline = True, log = False):
    """
    says if it a repository SVN
    
    @param      location        (str) location
    @param      commandline     (bool) use commandline or not
    @param      log             if True, return the log not a boolean
    @return                     bool
    """
    if location == None :
        location = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..", "..", "..")))
    try :
        r = get_repo_version(location, commandline, log = log)
        return True
    except Exception as e :
        if log :
            r = get_repo_version(location, commandline, log = log)
            return r
        else :
            return False

class RepoFile :
    """
    mimic a svn file
    """
    def __init__ (self, **args) :
        """
        constructor
        @param   args       list of members to add
        """
        for k,v in args.items() :
            self.__dict__[k] = v
            
    def __str__(self):
        """
        usual
        """
        return self.name

def repo_ls(full, commandline = True):
    """
    run ``ls`` on a path
    @param      full            full path
    @param      commandline use command line instead of pysvn
    @return                     output of client.ls
    """
    
    if not commandline :
        
        try :
            import pysvn
            client  = pysvn.Client()
            entry = client.ls (full)
            return entry
        except Exception as e :
            if "This client is too old to work with the working copy at" in str (e) or \
                "No module named 'pysvn'" in str(e) :
                cmd = "svn ls -r HEAD \"%s\"" % full.replace("\\","/")
                out,err = run_cmd(  cmd, 
                                    wait = True, 
                                    do_not_log = True, 
                                    encerror = "strict",
                                    encoding = sys.stdout.encoding if sys.stdout != None else "utf8")
                if len(err) > 0 :
                    fLOG ("problem with file ", full, err)
                    raise Exception(err)
                res = [ RepoFile(name=os.path.join(full,_.strip())) for _ in out.split("\n") if len(_) > 0]
                return res
            else :
                fLOG ("problem with file ", full, e)
                raise e
    else :
        cmd = "svn ls -r HEAD \"%s\"" % full.replace("\\","/")
        out,err = run_cmd(  cmd, 
                            wait = True, 
                            do_not_log = True, 
                            encerror = "ignore",
                            encoding = sys.stdout.encoding if sys.stdout != None else "utf8")
        if len(err) > 0 :
            fLOG ("problem with file ", full, err)
            raise Exception(err)
        res = [ RepoFile(name=os.path.join(full,_.strip())) for _ in out.split("\n") if len(_) > 0]
        return res
            
def __get_version_from_version_txt(path) :
    """
    private function, tries to find a file ``version.txt`` which should
    contains the version number (if svn is not present)
    @param      path        folder to look, it will look to the the path of this file,
                            some parents directories and finally this path
    @return                 the version number
    
    @warning If ``version.txt`` was not found, it throws an exception.
    """
    file = os.path.split(__file__)[0]
    pathes = [ file,
               os.path.join(file, ".."),
               os.path.join(file, "..", ".."),
               os.path.join(file, "..", "..", ".."),
               path ]
    for p in pathes :
        fp = os.path.join(p, "version.txt")
        if os.path.exists (fp) :
            with open(fp, "r") as f :
                return int(f.read().strip(" \n\r\t")) 
    raise FileNotFoundError("unable to find version.txt in\n" + "\n".join(pathes))
    
def get_repo_log (path = None, file_detail = False, commandline = True) :
    """
    get the latest changes operated on a file in a folder or a subfolder
    @param      path            path to look
    @param      file_detail     if True, add impacted files
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @return                     list of changes, each change is a list of 4-uple:
                                    - author
                                    - change number (int)
                                    - date (datetime)
                                    - comment
                    
    The function use a command line if an error occured. It uses the xml format:
    @code
    <logentry revision="161">
        <author>xavier dupre</author>
        <date>2013-03-23T15:02:50.311828Z</date>
        <msg>pyquickhelper: first version</msg>
    </logentry>
    @endcode
    """
    if path == None :
        path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..", "..")))
        
    if not commandline :
        try :
            import pysvn
            svnClient   = pysvn.Client()
            version = get_repo_version(path)
            log  = svnClient.log(
                    path, 
                    revision_start=pysvn.Revision( pysvn.opt_revision_kind.number, 0),
                    revision_end=pysvn.Revision( pysvn.opt_revision_kind.number, version ),
                    discover_changed_paths=True,
                    strict_node_history=True,
                    limit=0,
                    include_merged_revisions=False,
                    )
        except Exception as e :
            if "is not a working copy" in str(e) :
                return [
                        ("",
                         __get_version_from_version_txt(path),
                         datetime.datetime.now(),
                         "no repository") ]
            elif "This client is too old to work with the working copy at" in str (e) or \
                "No module named 'pysvn'" in str(e) :
                return get_repo_log(path,file_detail, commandline = True)
            else :
                raise e
                    
    else :
        cmd = "svn log -r HEAD:1 --xml \"%s\"" % path.replace("\\","/")
        out,err = run_cmd(  cmd, 
                            wait = True, 
                            do_not_log = True, 
                            encerror = "strict",
                            encoding = sys.stdout.encoding if sys.stdout != None else "utf8")
        if len(err) > 0 :
            fLOG ("problem with file ", path, err)
            raise Exception(err)
            
        root = ET.fromstring(out)
        res = []
        for i in root.iter('logentry'):
            revision    = int(i.attrib['revision'].strip())
            author      = i.find("author").text.strip()
            t           = i.find("msg").text
            msg         = t.strip() if t != None else "-"
            sdate       = i.find("date").text.strip()
            dt          = str_to_datetime(sdate.replace("T"," ").strip("Z "))
            row         = [author, revision, dt, msg ]
            res.append(row)
        return res
            
    message = []
    for info in log:
        message.append ( ( "",
                           info.revision.number, 
                           datetime.datetime.utcfromtimestamp(info.date),
                           info.message) )
        if file_detail :
            for i,pt in enumerate(info.changed_paths) :
                message.append( ("file",
                                 info.revision.numbe, 
                                 pt.data["action"], 
                                 pt.data["path"]) )
                if i > 100 :
                    message.append ("       ...")
                    break
            
    return message
            
def get_repo_version (path = None, commandline = True, log = False) :
    """
    get the latest check in number for a specific path
    @param      path            path to look
    @param      commandline     if True, use the command line to get the version number, otherwise it uses pysvn
    @param      log             if True, returns the output instead of a boolean
    @return                     integer (check in number)
    """
    if path == None :
        path = os.path.normpath(os.path.abspath( os.path.join( os.path.split(__file__)[0], "..", "..", "..")))
        
    if not commandline :
        try :
            import pysvn
            svnClient   = pysvn.Client()
            info        = svnClient.info2(".")
            infos       = [_[1] for _ in info ]
            revv        = [ _["rev"].number for _ in infos]
            revision    = max(revv)
            return revision
        except Exception as e :
            if "This client is too old to work with the working copy at" in str (e) or \
                "No module named 'pysvn'" in str(e) :
                return get_repo_version(path, commandline = True)
            elif "is not a working copy" in str(e) :
                return __get_version_from_version_txt(path)
            else :
                raise e
    else :
        cmd = "svn info -r HEAD" 
        if path != None : cmd += " \"%s\"" % path.replace("\\","/")
        out,err = run_cmd(  cmd, 
                            wait = True, 
                            do_not_log = True, 
                            encerror = "ignore",
                            encoding = sys.stdout.encoding if sys.stdout != None else "utf8",
                            log_error = False)
        if len(err) > 0 :
            if log: 
                fLOG ("problem with file ", path, err)
            if log :
                return "OUT\n{0}\nERR:{1}".format(out,err)
            else :
                raise Exception(err)
        lines = out.split("\n")
        lines = [ _ for _ in lines if "Revision" in _ ]
        lines = lines[0].split(":")
        res   = lines[1]
        
        if len(res) == 0 :
            o,e = run_cmd("svn help", wait = True, log_error = False)
            if len(o) < 3 :
                raise Exception("the command 'svn help' should return something")
                
        return int(res)
            
def get_master_location(path = None, commandline = True):
    """
    raises an exception
    """
    raise NotImplementedError()
    
    