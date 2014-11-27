#-*- coding: utf-8 -*-
"""
@file

@brief Exception specific to this module


The function fLOG (or fLOG) is used to logged everything into a log file.

@code
from pyquickhelper.loghelper.flog import fLOG
fLOG (OutputPrint = True)                 # the logs are also displayed in the output stream
fLOG (LogPath     = "...")                # chanages the path returned by GetPath
fLOG ("un", "deux", 4, ["gt"])            # log everything in a log file

from pyquickhelper.loghelper.flog import GetPath ()
print GetPath ()                            # return the log path (file temp_log.txt)

fLOG (LogPath = "c:/temp/log_path")       # change the log path, creates it if it does not exist
@endcode

@warning This module inserts static variable in module sys. I did it because I did not know how to deal with several instance of the same module.
"""

import datetime,sys,os,time, subprocess, random, math, decimal, urllib, copy
import urllib.request

class PQHException (Exception) :
    """
    custom exception for this file
    """
    pass


def init (path = None, filename = None, create = True, path_add = None) :
    """
    initialisation
    @param      path            new path,
                                    - if path == "###", then uses d:\\temp\\log_pyquickhelper is it exists or c:\\temp\\log_pyquickhelper if not
    @param      filename        new filename
    @param      create          force the creation
    @param      path_add        subfolder to append to the current folder

    This function is also called when LogPath is specified while calling function fLOG.
    """
    if path_add is None:
        path_add=[]
    if path is None :
        path = sys.hal_log_values ["__log_path"]

    if path == "###" :
        if sys.platform.startswith("win") :
            path = "d:\\temp" if os.path.exists ("d:\\temp") else "c:\\temp"
            path = os.path.join (path, "log_pyquickhelper")
        else :
            path = "/tmp"
            path = os.path.join (path, "log_pyquickhelper")

    if len (path_add) > 0 :
        if not isinstance (path_add, list) : path_add = [ path_add ]
        temp = []
        for p in path_add :
            spl = os.path.splitext (p)
            temp.append (spl [0])
        path = os.path.join (path, *temp)

    if filename is None :
        filename = sys.hal_log_values ["__log_file_name"]

    if (sys.hal_log_values ["__log_path"] != path or sys.hal_log_values ["__log_file_name"] != filename) \
          and sys.hal_log_values ["__log_file"] is not None :
        sys.hal_log_values ["__log_file"].close ()
        sys.hal_log_values ["__log_file"] = None
    sys.hal_log_values ["__log_path"]       = path
    sys.hal_log_values ["__log_file_name"]  = filename

    if create :
        if not os.path.exists (sys.hal_log_values ["__log_path"]) :
            os.makedirs (sys.hal_log_values ["__log_path"])
    else :
        if not os.path.exists (sys.hal_log_values ["__log_path"]) :
            raise PQHException ("unable to find path " + sys.hal_log_values ["__log_path"])

def GetSepLine () :
    """
    return always ``\\n``
    """
    return "\n" # previous value: sys.hal_log_values ["__log_file_sep"]

def GetPath () :
    """
    returns a path where the log file is stored.
    @return         path to the logs
    """
    return sys.hal_log_values ["__log_path"]

def Print (redirect = True) :
    """
    if True, redirect everything which is displayed to the standard output
    """
    lock = sys.hal_log_values.get("Lock", False)
    if not lock :
        sys.hal_log_values ["__log_display"] = redirect

class LogFakeFileStream:
    """
    a fake file
    """
    def __init__(self):
        """
        do nothing
        """
        pass

    def open(self):
        """
        do nothing
        """
        pass

    def write(self, s):
        """
        do nothing
        """
        pass

    def close(self):
        """
        do nothing
        """
        pass

    def flush(self):
        """
        do nothing
        """
        pass

def GetLogFile (physical = False) :
    """
    Returns a file name containing the log

    @param      physical    use a physical file or not
    @return                 a pointer to a log file
    @rtype                  str
    @exception  OSError     if this file cannot be created
    """
    if sys.hal_log_values ["__log_file"] is None :
        if physical :
            path = GetPath ()
            if sys.hal_log_values ["__log_file_name"] is None :
                if os.path.exists (path) :  sys.hal_log_values ["__log_file_name"] = os.path.join (path, sys.hal_log_values ["__log_const"])
                else :                      raise PQHException ("unable to create a log file in folder " + path)

            if not isinstance (sys.hal_log_values ["__log_file_name"], str) :
                sys.hal_log_values ["__log_file"] = sys.hal_log_values ["__log_file_name"]
            else :
                try :
                    sys.hal_log_values ["__log_file"] = open (sys.hal_log_values ["__log_file_name"], "w", encoding="utf-8")
                except Exception as e:
                    raise OSError ("unable to create file " + sys.hal_log_values ["__log_file_name"] + "\n" + str(e))
        else :
            sys.hal_log_values ["__log_file"] = LogFakeFileStream()

    return sys.hal_log_values ["__log_file"]

def noLOG (*l, **p) :
    """
    does nothing
    """
    pass

def fLOG (*l, **p) :
    """
    Builds a message on a single line with the date, it deals with encoding issues.

    @param      l       list of fields
    @param      p       dictionary of fields
                            - if p contains OutputPrint, call Print (OutputPrint),
                            - if p contains LogPath, it calls init (v)
                            - if p contains LogFile, it changes the log file name (it creates a new one, the previous is closed).
                            - if p contains LogPathAdd, it adds this path to the temporary file
                            - if p contains Lock, it Locks option OutputPrint
                            - if p contains UnLock, it unlock option OutputPrint

                        example:
                        @code
                        fLOG (LogPath = "###", LogPathAdd = __file__, OutputPrint = True)
                        @endcode

    @exception  OSError     When the log file cannot be created.

    @example(activate the logs)
    @code
    fLOG(OutputPrint=True)
    @endcode
    @endexample

    @FAQ(How to activate the logs?)
    The following instruction will do:
    @code
    fLOG(OutputPrint=True)
    @endcode

    To log everything into a file:
    @code
    fLOG(OutputPrint=True, LogFile="log_file.txt")
    @endcode

    @endFAQ
    """
    path_add = p.get ("LogPathAdd", [] )

    lock = p.get("Lock", None)
    if lock is not None : sys.hal_log_values["Lock"] = lock

    if "LogFile" in p and "LogPath" in p :  init (p ["LogPath"], p ["LogFile"])
    elif "LogFile" in p :                   init (filename = p ["LogFile"], path_add = path_add)
    elif "LogPath" in p :                   init (path     = p ["LogPath"], path_add = path_add)

    def myprint(s): print(s)

    if "OutputPrint" in p :
        Print (p ["OutputPrint"])

    if "LogFile" in p :
        logfile = GetLogFile(True)

    dt = datetime.datetime (2009,1,1).now ()
    if len (l) > 0 :
        def _str_process (s) :
            if isinstance (s, str) : return s
            elif isinstance(s, bytes) : return s.decode("utf8")
            else :
                try:
                    return str (s)
                except Exception as e :
                    raise Exception("unable to convert s into string: type(s)=" + str(type(s))) from e

        message = str (dt).split (".")[0] + " " + " ".join ( [_str_process(s)  for s in l ] ) + sys.hal_log_values ["__log_file_sep"]

        if sys.hal_log_values ["__log_display"] :
            try :
                myprint (message.strip ("\r\n"))
            except UnicodeEncodeError :
                try :
                    myprint ("\n".join (repr (message.strip ("\r\n")).split ("\\n")))
                except UnicodeEncodeError :
                    try :
                        rr = repr (message.strip ("\r\n")).split ("\\n")
                        for r in rr :
                            myprint (r.encode("utf8"))
                    except UnicodeEncodeError :
                        myprint ("look error in log file")
        GetLogFile ().write (message)
        st = "                    "
    else :
        st = str (dt).split (".")[0] + " "

    for k,v in p.items () :
        if k == "OutputPrint" and v : continue
        message = st + "%s = %s%s" % (str (k), str (v), sys.hal_log_values ["__log_file_sep"])
        if "INNER JOIN" in message :
            break
        GetLogFile ().write (message)
        if sys.hal_log_values ["__log_display"] :
            try :
                myprint (message.strip ("\r\n"))
            except UnicodeEncodeError :
                myprint ("\n".join (repr (message.strip ("\r\n")).split ("\\n")))
    GetLogFile ().flush ()

def get_relative_path (folder, file) :
    """
    return the relative path between a folder and a file

    @param      folder      folder
    @param      file        file
    @return                 relative path
    @rtype                  str
    """
    if not os.path.exists (folder) : raise PQHException (folder + " does not exist.")
    if not os.path.exists (file)   : raise PQHException (file + " does not exist.")
    sd = folder.replace("\\","/").split("/")
    sf = file.replace("\\","/").split("/")
    for i in range (0, len (sd)) :
        if i >= len (sf) : break
        elif sf [i] != sd [i] : break
    res = copy.copy (sd)
    j = i
    while i < len (sd) :
        i += 1
        res.append ("..")
    res.extend (sf [j:])
    return os.path.join (*res)

def download (httpfile, path_unzip = None, outfile = None) :
    """
    Download a file to the folder path_unzip if not present, if the downloading is interrupted,
    the next time, it will start from where it stopped. Before downloading, the function creates a temporary file,
    which means the downloading has began. If the connection is lost, an exception is raised and the program stopped.
    Next time, the program will detect the existence of the temporary file and will start downloading from where it previously stopped.
    After it ends, the temporary file is removed.

    @param      httpfile        (str) url
    @param      path_unzip      (str) path where to unzip the file, if None, choose GetPath ()
    @param      outfile         (str) if None, the function will assign a filename unless this parameter is specified
    @return                     local file name
    """
    if path_unzip is None : path_unzip = GetPath ()
    file = _check_source (httpfile, path_unzip = path_unzip, outfile = outfile)
    return file

def unzip (file, path_unzip = None, outfile = None) :
    """
    unzip a file into the temporary folder
    @param      file            (str) zip files
    @param      path_unzip      (str) where to unzip the file, if None, choose GetPath ()
    @param      outfile         (str) if None, the function will assign a filename unless this parameter is specified
    @return                     expanded file name
    """
    if path_unzip is None : path_unzip = GetPath ()
    fLOG ("unzip file", file)
    file = _check_source (file, path_unzip = path_unzip, outfile = outfile)

    nb = 0
    while not os.path.exists (file) and nb < 10 :
        time.sleep(0.5)
        nb += 1

    if not os.path.exists (file) :
        raise FileNotFoundError(file)

    return file

def _get_file_url (url, path) :
    """build a filename knowing an url
    @param      url         url
    @param      path        where to download the file
    @return                 filename
    """
    path = path + "/" + url.replace ("/", "!").replace (":","").replace (".","-")
    spl  = path.split ("-")
    if len (spl) >= 2 :
        ext = spl [len (spl)-1].lower ()
        if 2 <= len (ext) <= 3 and ext in ["png", "jpg", "zip", "txt", "gif", "py", "cpp", "gz", "pdf", "tif", "py", "html", "h"] :
            spl  = path.split ("-")
            spl  = spl [:len(spl)-1]
            path = "-".join (spl) + "." + ext
    return path

def _get_file_txt (zipname) :
    """
    build a filename knowing an url, same name but in default_path
    @param      zipname     filename of the zip
    @return                 filename
    """
    file = os.path.split (zipname) [1]
    file = file.replace (".zip", ".txt")
    file = file.replace (".ZIP", ".txt")
    file = file.replace (".gz", ".txt")
    file = file.replace (".GZ", ".txt")
    return file

def _check_zip_file (filename, path_unzip, outfile) :
    """
    this function tests if a file is a zip file (extension zip),
    if it is the case, it unzips it into another file and return the new name,
    if the unzipped file already exists, the file is not unzipped a second time

    @param      filename        any filename (.zip or not), if txt, it has no effect
    @param      path_unzip      if None, unzip it where it stands, otherwise, place it into path
    @param      outfile         if None, the function will assign a filename unless this parameter is specified
    @return                     the unzipped file or filename if the format was not zip
    """
    assert path_unzip is not None
    file,ext = os.path.splitext (filename)
    ext      = ext.lower ()
    if ext == ".gz" :

        import gzip

        if outfile is None :
            dest = filename.split ("!")
            dest = dest [ len(dest)-1 ]
            ext  = os.path.splitext (dest) [1]
            dest = dest.replace (ext, ".txt")
            path = os.path.split (filename)
            path = "/".join (path [:len (path)-1])
            dest = path + "/" + dest
        else :
            dest = outfile

        if not os.path.exists (dest) :
            file = gzip.GzipFile (filename, "r")
            if outfile is None :
                dest = os.path.split (dest) [1]
                dest = os.path.join (path_unzip, dest)

            if os.path.exists (dest) :
                st1 = datetime.datetime.utcfromtimestamp (os.stat (filename).st_mtime)
                st2 = datetime.datetime.utcfromtimestamp (os.stat (dest).st_mtime)
                if st2 > st1 :
                    fLOG ("ungzipping file (already done)", dest)
                    return dest

            fLOG ("ungzipping file", dest)
            f    = open (dest, "w")
            data = file.read (2**27)
            size = 0
            while len (data) > 0 :
                size += len (data)
                fLOG ("ungzipping ", size, "bytes")
                if isinstance (data, bytes) : f.write (bytes.decode (data))
                else : f.write (data)
                data = file.read (2**27)
            f.close ()
            file.close ()

        return dest

    if ext == ".zip" :

        import zipfile
        try :
            file = zipfile.ZipFile (filename, "r")
        except Exception as e :
            fLOG ("problem with ", filename)
            raise e

        if len (file.infolist()) != 1:
            if outfile is not None :
                raise PQHException ("the archive contains %d files and not one as you expected by filling outfile" % len (file.infolist()))
            fLOG ("unzip file (multiple) ", filename)
            #message = "\n".join ([ fi.filename for fi in file.infolist() ] )
            #raise Exception.YstException("ColumnInfoSet.load_from_file: file %s contains no file or more than one file\n" + message)
            folder = os.path.split (filename) [0]
            todo   = 0
            _zip7_path = r"c:\Program Files\7-Zip"
            zip7   = os.path.exists (_zip7_path)
            wait   = [ ]
            for info in file.infolist () :
                fileinside  = info.filename
                dest        = os.path.join (folder, fileinside)
                if not os.path.exists (dest) :
                    fol = os.path.split (dest) [0]
                    if not os.path.exists (fol) : os.makedirs (fol)
                    if os.path.exists (dest) :
                        st1 = datetime.datetime.utcfromtimestamp (os.stat (filename).st_mtime)
                        st2 = datetime.datetime.utcfromtimestamp (os.stat (dest).st_mtime)
                        if st2 > st1 :
                            continue

                    if not sys.platform.startswith("win") or not zip7 :
                        data = file.read (fileinside)
                        dest = os.path.split (dest) [1]
                        dest = os.path.join (path_unzip, dest)
                        fLOG ("unzipping file", dest)
                        wait.append(dest)
                        f    = open (dest, "w")
                        if isinstance (data, bytes) :
                            f.write (str (data))
                        else :
                            f.write (data)
                        f.close ()
                    else :
                        todo += 1

            if todo > 0 and zip7 :
                dest    = os.path.realpath (path_unzip)
                cmd     = '"' + _zip7_path + '\\7z.exe" e -y -o"%s" "%s"' % (dest, os.path.realpath (filename))
                out,err = run_cmd (cmd, wait = True)
                if len (err) > 0 :  raise PQHException ("command {0} failed\n{1}".format(cmd,err))
                if "Error" in out : raise PQHException ("command {0} failed\n{1}".format(cmd,out))
            else :
                dest    = path_unzip

            file.close ()

            ch = False
            while not ch :
                ch = True
                for a in wait :
                    if not os.path.exists(a) :
                        ch = False
                        break
                time.sleep(0.5)

            return dest

        else :
            for info in file.infolist () :
                fileinside = info.filename

            path = os.path.split (filename)
            dest = outfile if outfile is not None else path [0] + "/" + fileinside
            if not os.path.exists (dest) :
                data = file.read (fileinside)
                if outfile is None :
                    dest = os.path.split (dest) [1]
                    dest = os.path.join (path_unzip, dest)

                if os.path.exists (dest) :
                    st1 = datetime.datetime.utcfromtimestamp (os.stat (filename).st_mtime)
                    st2 = datetime.datetime.utcfromtimestamp (os.stat (dest).st_mtime)
                    if st2 > st1 :
                        fLOG("unzipping one file (already done)", dest)
                        return dest

                fLOG("unzipping one file", dest)
                f    = open (dest, "w")
                if isinstance (data, bytes) :
                    f.write (bytes.decode (data))
                else :
                    f.write (data)
                f.close ()
                file.close ()
            return dest

    return filename

def _first_more_recent (f1, path) :
    """
    checks if the first file (opened url) is more recent of the second file (path)
    @param      f1      opened url
    @param      path    path name
    @return             boolean
    """
    import datetime
    import re
    import time
    s = str (f1.info ())
    da = re.compile ("Last[-]Modified: (.+) GMT").search (s)
    if da is None :
        return True

    da = da.groups () [0]
    gr = re.compile ("[\w, ]* ([ \d]{2}) ([\w]{3}) ([\d]{4}) ([\d]{2}):([\d]{2}):([\d]{2})").search (da)
    if gr == None : return True
    gr = gr.groups ()
    da = datetime.datetime ( int (gr [2]), sys.hal_log_values ["month_date"] [gr [1].lower ()], int (gr [0]),
                             int (gr [3]), int (gr [4]), int (gr [5]) )

    p  =  time.ctime (os.path.getmtime (path))
    gr = re.compile ("[\w, ]* ([\w]{3}) ([ \d]{2}) ([\d]{2}):([\d]{2}):([\d]{2}) ([\d]{4})").search (p)
    if gr is None :
        return True
    gr = gr.groups ()
    da = datetime.datetime ( int (gr [5]), sys.hal_log_values ["month_date"] [gr [0].lower ()], int (gr [1]),
                             int (gr [2]), int (gr [3]), int (gr [4]) )

    file = da

    return da > file

def _check_url_file (url, path_download, outfile) :
    """if url is an url, download the file and return the downloaded
    if it has already been downloaded, it is not downloaded again
    @param      url                 url
    @param      path_download       download the file here
    @param      outfile             if None, the function will assign a filename unless this parameter is specified
    @return                         the filename
    """
    if "http://" in url.lower () :
        dest = outfile if outfile is not None else _get_file_url (url, path_download)
        down = False
        nyet = dest + ".notyet"

        if os.path.exists (dest) and not os.path.exists (nyet) :
            try :
                fLOG("trying to connect", url)
                f1      = urllib.urlopen (url)
                down    = _first_more_recent (f1, dest)
                newdate = down
                f1.close ()
            except IOError :
                fLOG("unable to connect Internet, working offline for url", url)
                down = False
        else :
            down    = True
            newdate = False

        if down :
            if newdate :    fLOG (" downloading (updated) ", url)
            else :          fLOG (" downloading ", url)

            if len (url) > 4 and url [-4].lower () in [".txt", ".csv", ".tsv", ".log"] :
                fLOG ("creating text file ", dest)
                format = "w"
            else :
                fLOG ("creating binary file ", dest)
                format = "wb"

            if os.path.exists (nyet) :
                size    = os.stat (dest).st_size
                fLOG ("resume downloading (stop at", size, ") from ", url)
                request = urllib.request.Request(url)
                request.add_header("Range", "bytes=%d-" % size)
                fu      = urllib.request.urlopen (request)
                f       = open (dest, format.replace ("w", "a"))
            else :
                fLOG ("downloading ", url)
                request = urllib.request.Request(url)
                fu      = urllib.request.urlopen (url)
                f       = open (dest, format)

            open (nyet, "w").close ()
            c       = fu.read (2**21)
            size    = 0
            while len (c) > 0 :
                size += len (c)
                fLOG("    size", size)
                f.write (c)
                f.flush ()
                c = fu.read (2**21)
            fLOG ("end downloading")
            f.close ()
            fu.close ()
            os.remove (nyet)

        url = dest
    return url

def _check_source (fileurl, path_unzip, outfile) :
    """
    @param      fileurl     can be an url, a zip file, a text file
    @param      path_unzip  if None, unzip the file where it stands, otherwise, put it in path
    @param      outfile     if None, the function will assign a filename unless this parameter is specified
    @return                 a text file name

    if it is:
        - an url:       download it and copy it into default_path
        - a zipfile:    beside the true file
        - a text file:  do nothing

    If the file has already been downloaded and unzipped, it is not done twice.
    """
    if outfile is not None and os.path.splitext (outfile)[1].lower () == os.path.splitext (fileurl)[1].lower () :
        file = _check_url_file (fileurl,    path_download   = path_unzip, outfile = outfile)
        return file
    else :
        file = _check_url_file (fileurl,    path_download   = path_unzip, outfile = None)
        txt  = _check_zip_file (file,       path_unzip      = path_unzip, outfile = outfile)
        if not os.path.exists (txt):
            message = "hal_core._check_source: unable to find file " + txt + " source (" + fileurl + ")"
            raise PQHException (message)
        return txt

def get_interpreter_path () :
    """
    return the interpreter path
    """
    if sys.platform.startswith("win") : return sys.executable.replace ("pythonw.exe", "python.exe")
    else : return sys.executable

def split_cmp_command(cmd, remove_quotes = True) :
    """
    splits a command line
    @param      cmd             command line
    @param      remove_quotes   True by default
    @return                     list
    """
    if isinstance (cmd, str) :
        spl = cmd.split()
        res = []
        for s in spl :
            if len(res) == 0 :
                res.append(s)
            elif res[-1].startswith('"') and not res[-1].endswith('"') :
                res[-1] += " " + s
            else :
                res.append(s)
        if remove_quotes :
            nres = [ ]
            for _ in res :
                if _.startswith('"') and _.endswith('"'):
                    nres.append(_.strip('"'))
                else:
                    nres.append(_)
            return nres
        else:
            return res
    else :
        return cmd

def decode_outerr(outerr, encoding, encerror, msg):
    """
    decode the output or the error after running a command line instructions

    @param      outerr      output or error
    @param      encoding    encoding
    @param      encerror    how to handle errors
    @param      msg         part of the error to add message
    @return                 converted string
    """
    if not isinstance(outerr,bytes):
        raise TypeError("only able to decode bytes, not " + str(type(outerr)))
    try :
        out = outerr.decode(encoding, errors=encerror)
        return out
    except UnicodeDecodeError as exu :
        try :
            out = outerr.decode("utf8" if encoding != "utf8" else "latin-1", errors=encerror)
            return out
        except Exception as e :
            out = outerr.decode(encoding, errors='ignore')
            raise Exception("issue with cmd (" + encoding +"):" + str(msg) + "\n" + str(exu) + "\n-----\n" + out) from e
    raise Exception("complete issue with cmd:" + str(msg))

def run_cmd (   cmd,
                sin             = "",
                shell           = True,
                wait            = False,
                log_error       = True,
                secure          = None,
                stop_waiting_if = None,
                do_not_log      = False,
                encerror        = "ignore",
                encoding        = "utf8",
                change_path     = None,
                communicate     = True,
                preprocess      = True,
                timeout         = None) :
    """
    run a command line and wait for the result
    @param      cmd                 command line
    @param      sin                 sin: what must be written on the standard input
    @param      shell               if True, cmd is a shell command (and no command window is opened)
    @param      wait                call ``proc.wait``
    @param      log_error           if log_error, call fLOG (error)
    @param      secure              if secure is a string (a valid filename), the function stores the output in a file
                                    and reads it continuously
    @param      stop_waiting_if     the function stops waiting if some condition is fulfilled.
                                    The function received the last line from the logs.
    @param      do_not_log          do not log the output
    @param      encerror            encoding errors (ignore by default) while converting the output into a string
    @param      encoding            encoding of the output
    @param      change_path         change the current path if  not None (put it back after the execution)
    @param      communicate         use method `communicate <https://docs.python.org/3.4/library/subprocess.html#subprocess.Popen.communicate>`_ which is supposed to be safer,
                                    parameter ``wait`` must be True
    @param      preprocess          preprocess the command line if necessary (not available on Windows) (False to disable that option)
    @param      timeout             when data is sent to stdin (``sin``), a timeout is needed to avoid waiting for ever
    @return                         content of stdout, stdres  (only if wait is True)
    @rtype      tuple

    @example(run a program using the command line)
    @code
    out,err = run_cmd( "python setup.py install", wait=True)
    @endcode
    @endexample

    If you are using this function to run git function, parameter ``shell`` must be True.

    .. versionchanged:: 0.9
        parameter *timeout* was added,
        the function now works with stdin
    """
    if secure is not None :
        with open(secure,"w") as f : f.write("")
        add = ">%s" % secure
        if isinstance (cmd, str) : cmd += " " + add
        else : cmd.append(add)
    if not do_not_log :
        fLOG ("execute ", cmd)

    if change_path is not None :
        current = os.getcwd()
        os.chdir(change_path)

    if sys.platform.startswith("win") :

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        pproc = subprocess.Popen (cmd,
                                 shell = shell,
                                 stdin  = subprocess.PIPE if sin is not None and len(sin) > 0 else None,
                                 stdout = subprocess.PIPE if wait else None,
                                 stderr = subprocess.PIPE if wait else None,
                                 startupinfo = startupinfo)
    else :
        cmdl = split_cmp_command(cmd) if preprocess else cmd
        if not do_not_log :
            fLOG("--linux", cmdl)
        pproc = subprocess.Popen (cmdl,
                                 shell  = shell,
                                 stdin  = subprocess.PIPE if sin is not None and len(sin) > 0 else None,
                                 stdout = subprocess.PIPE if wait else None,
                                 stderr = subprocess.PIPE if wait else None)

    if isinstance(cmd, list):
        cmd = " ".join(cmd)

    if wait :

        out = [ ]
        skip_waiting = False

        if communicate:
            stdoutdata, stderrdata = pproc.communicate(sin if sin is None else sin.encode(), timeout = timeout)
            out = decode_outerr(stdoutdata, encoding, encerror, cmd)
            err = decode_outerr(stderrdata, encoding, encerror, cmd)
        else :
            if sin is not None and len(sin) > 0 :
                raise Exception("communicate should be True to send something on stdin")
            stdout, stderr = pproc.stdout, pproc.stderr

            if secure is None :
                for line in stdout :
                    decol = decode_outerr(line, encoding, encerror, cmd)
                    if not do_not_log :
                        fLOG(decol.strip("\n\r"))

                    out.append(decol.strip("\n\r"))
                    if stdout.closed: break
                    if stop_waiting_if is not None and stop_waiting_if(decol) :
                        skip_waiting = True
                        break
            else :
                last = []
                while pproc.poll() is None :
                    if os.path.exists (secure) :
                        with open(secure,"r") as f :
                            lines = f.readlines()
                        if len(lines) > len(last) :
                            for line in lines[len(last):] :
                                fLOG(line.strip("\n\r"))
                                out.append(line.strip("\n\r"))
                            last = lines
                        if stop_waiting_if is not None and len(last)>0 and stop_waiting_if(last[-1]) :
                            skip_waiting = True
                            break
                    time.sleep(0.1)

            if not skip_waiting :
                pproc.wait ()

            out = "\n".join(out)
            temp = err = stderr.read()
            try:
                err = decode_outerr(temp, encoding, encerror, cmd)
            except :
                err = decode_outerr(temp, encoding, "ignore", cmd)

            stdout.close()
            stderr.close()

        err = err.replace("\r\n","\n")
        if not do_not_log : fLOG ("end of execution ", cmd)
        if len (err) > 0 and log_error : fLOG ("error (log)\n%s" % err)

        if change_path is not None :
            os.chdir(current)

        if sys.platform.startswith("win") :
            return out.replace("\r\n","\n"), err.replace("\r\n","\n")
        else:
            return out, err
    else :

        if change_path is not None :
            os.chdir(current)

        return "",""

def run_script (script, *l) :
    """
    run a script
    @param      script      script to execute
    @param      l           other parameters
    @return                 out,err: content of stdout stream and stderr stream
    """
    if not os.path.exists (script) :
        raise PQHException ("file %s not found" % script)
    py  = get_interpreter_path ()
    cmd = "%s %s" % (py, script)
    if len (l) > 0 :
        cmd += " " + " ".join ( [str (x) for x in l])
    out,err = run_cmd (cmd)
    return out,err

def get_prefix () :
    """
    return a prefix for a file based on time
    """
    t = datetime.datetime (2010,1,1).now ()
    t = str(t).replace (":", "_").replace ("/", "_").replace (" ", "_")
    t += "_" + str (random.randint (0,1000)) + "_"
    return os.path.join (GetPath (), "temp_" + t)

def removedirs (folder, silent = False) :
    """
    remove all files and folder in folder
    @param      folder      folder
    @param      silent      silent mode or not
    @return                 list of not remove files or folders
    """
    file, rep = [], []
    for r, d, f in os.walk (folder) :
        for a in d :
            rep.append (os.path.join (r, a))
        for a in f :
            file.append (os.path.join (r, a))
    impos = []
    file.sort ()
    rep.sort (reverse = True)
    for f in file :
        try :
            if os.path.exists (f):
                os.remove (f)
        except Exception as e :
            fLOG ("unable to remove file", f, " --- ", str(e).replace("\n", " "))
            if silent :  impos.append (f)
            else : raise
    for f in rep :
        try :
            if os.path.exists (f):
                os.removedirs (f)
        except Exception as e :
            fLOG ("unable to remove folder", f, " --- ", str(e).replace("\n", " "))
            if silent :  impos.append (f)
            else : raise

    if os.path.exists (folder) :
        try :
            os.rmdir(folder)
        except Exception as e:
            impos.append(folder)
    return impos

def guess_type_value (x, none = None) :
    """
    guess the type of a value
    @param      x           type
    @param      none        if True and all values are empty, return None
    @return                 type

    @warning if an integer starts with a zero, then it is a string
    """
    try :
        int (x)
        if x [0] == '0' and len (x) > 1 :   return str
        else :                              return int if len (x) < 9 else str
    except :
        try :
            x = float (x)
            return float
        except :
            if none :
                if x is None : return None
                try :
                    if len (x) > 0 : return str
                    else : return None
                except :
                    return None
            else :
                return str

def guess_type_value_type (none = True) :
    """
    @param      none        if True and all values are empty, return None
    @return                 the list of types recognized by guess_type_value
    """
    return [ None, str, int, float ] if none else [ str, int, float ]

def get_default_value_type (ty, none = True) :
    """
    @param      ty          type in guess_type_value_type
    @param      none        if True and all values are empty, return None
    @return                 a default value for this type
    """
    if      ty is None and none : return None
    elif    ty == str   : return ""
    elif    ty == int       : return 0
    elif    ty == decimal.Decimal : return decimal.Decimal(0)
    elif    ty == float     : return 0.0
    else :
        raise PQHException ("type expected in " + str (guess_type_value_type ()))

def guess_type_list (l, tolerance = 0.01, none = True) :
    """
    guess the type of a list
    @param      l           list
    @param      tolerance   let's denote m as the frequency of the most representative type,
                            and m2 the second one, if m2 > m * tolerance --> str
    @param      none        if True and all values are empty, return None
    @return                 type, length (order of preference (int, float, str))
                            the parameter length has a meaning only for str result
    """
    defa   = None if none else str
    length = 0

    if l in [str, float, int, None, decimal.Decimal] :
        raise PQHException ("this case is unexpected %s" % str (l))

    if len (l) == 0 :
        res = defa

    elif len (l) == 1 :
        res = guess_type_value (l[0], none)
        if res == str :
            length = len (l [0])

    else :
        count = { }
        for x in l :
            t = guess_type_value (x, none)
            length = max (length, len (x))
            if t in count : count [t] += 1
            else :          count [t]  = 1

        val = [ (v,k) for k,v in count.items() ]
        val.sort (reverse = True)
        if len (val) == 1 :
            res = val [0][1]
        elif val [0][0] * tolerance < val [1][0] :
            res = str
        else :
            res = val [0][1]

    if res != str :
        olength = 0
    else :
        if length > 0 :
            x = math.log (length) / math.log (2) + 0.99999
            x = int (x)
            olength = math.exp ( x * math.log (2)) +  0.9999
            olength = int (olength)*2
        else :
            olength = length

    return res, olength

def guess_machine_parameter () :
    """
    determine many parameters on this machine
        - machine name
        - user name
        - domain...
    @return         dictionary { name : value }
    """
    val = [ "COMPUTERNAME", "NUMBER_OF_PROCESSORS", "OS",
            "PATH", "USERDOMAIN", "USERNAME", "USERPROFILE",
            "windir", "TEMP" ]
    res = { }
    for v in val :
        if v == "PATH" :
            x = os.getenv (v)
            x = x.split (";")
            res [v] = x
        else : res [v] = os.getenv (v)

    if not sys.platform.startswith("win") :
        if "TEMP" not in res or res["TEMP"] is None :
            res["TEMP"] = "/tmp"

    return res

def IsEmptyString (s) :
    """
    empty string or not?

    @param      s               any string (str, None)
    @return                     is it empty or not?
    @rtype      bool
    @exception  PQHException    When a type is unexpected
    """
    if s is None : return True
    elif isinstance (s, str) :
        return len (s) == 0
    else :
        raise PQHException ("the type is unexpected %s" % str (type (s)))

def load_content_file_with_encoding (filename) :
    """
    try different encoding to load a file, tries utf8, latin1 and None
    @param      filename    filename
    @return                 couple  (content, encoding)
    """
    error = None
    for enc in [ "utf8", "latin1", None ] :
        try :
            with open(filename, "r", encoding = enc) as f : content = f.read()
            return content, enc
        except Exception as e :
            error = e
    raise error

if "hal_log_values" not in sys.__dict__ :
    sys.hal_log_values = dict()
    sys.hal_log_values ["__log_const"]     = "temp_log.txt"
    sys.hal_log_values ["__log_path"]      = "."
    sys.hal_log_values ["__log_file_name"] = None
    sys.hal_log_values ["__log_file"]      = None
    sys.hal_log_values ["__log_file_sep"]  = "\n"  # previous value: "\n" if not sys.platform.startswith("win") else "\n"
    sys.hal_log_values ["__log_display"]   = False
    sys.hal_log_values ["month_date"]      = {"jan":1, "feb":2, "mar":3, "apr":4, "may":5, "jun":6, "jul":7, "aug":8, "sep":9, "oct":10, "nov":11, "dec":12 }