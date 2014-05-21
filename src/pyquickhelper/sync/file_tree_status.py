#-*- coding: utf-8 -*-
"""
@file

@brief      keep the status of a folder, assuming this folder is not moved
"""

import os, re, datetime, time, shutil, hashlib


from ..loghelper.pqh_exception  import PQHException
from ..loghelper.flog           import fLOG
from ..loghelper.pyrepo_helper  import SourceRepository

def convert_st_date_to_datetime (t) :
    """
    converts a string into a datetime
    
    @param      t       str
    @return             datetime
    """
    if isinstance (t, str) :
        if "." in t : 
            return datetime.datetime.strptime (t, "%Y-%m-%d %H:%M:%S.%f")
        else :
            return datetime.datetime.strptime (t, "%Y-%m-%d %H:%M:%S")
    else :
        return datetime.datetime.fromtimestamp(t)
        
def checksum_md5 (filename) :
    """
    computes MD5 for a file
    
    @param      filename        filename
    @return                     string or None if there was an error
    """
    fname = filename
    block_size = 0x10000
    def upd(m, data):
        m.update(data)
        return m
    fd = open(fname, "rb")
    try:
        block = [ fd.read(block_size) ]
        while len(block[-1]) > 0 :
            block.append ( fd.read(block_size) )
        contents = block
        zero =  hashlib.md5()
        i = 0 
        for el in contents :
            i += 1
            zero.update( el )
        m = zero
        return m.hexdigest()
    finally:
        fd.close()
    return None        

class FileInfo :
    """
    intermediate class: it represents the data we collect about a file
    to determine whether or not it was modified
    """
    
    def __init__ (self, filename, size, date, mdate, checksum) :
        """
        constructor
        
        @param      filename        filename
        @param      size            size
        @param      date            date (str or datetime)
        @param      mdate           modification date (str or datetime)
        
        Dates will be converted into datetime.
        """
        self.filename   = filename
        self.size       = size
        self.date       = date
        self.mdate      = mdate    # modification date
        self.checksum   = checksum
        if date != None and not isinstance (self.date, datetime.datetime) :
            raise ValueError("mismatch for date (%s) and file %s" % (str(type(date)), filename))
        if mdate != None and not isinstance (self.mdate, datetime.datetime) :
            raise ValueError("mismatch for mdate (%s) and file %s" % (str(type(mdate)), filename))
        if not isinstance (size, int) :
            raise ValueError("mismatch for size (%s) and file %s" % (str(type(size)), filename))
        if checksum != None and not isinstance (checksum, str) :
            raise ValueError("mismatch for checksum (%s) and file %s" % (str(type(checksum)), filename))
        if date != None and mdate != None :
            if mdate > date :
                raise ValueError("expecting mdate <= date for file " + file)
            
    def __str__ (self) :
        """
        usual
        """
        return "File[name=%s, size=%d (%s), mdate=%s (%s), date=%s (%s), md5=%s (%s)]" % \
                 (self.filename, \
                    self.size, str(type(self.size)), \
                  str(self.mdate), str(type(self.mdate)), \
                  str(self.date), str(type(self.date)), \
                  self.checksum, str(type(self.checksum)))
        
    def set_date(self, date) :
        """
        set date
        
        @param  date    date (a str or datetime)
        """
        self.date = date
        if not isinstance (self.date, datetime.datetime) :
            raise ValueError("mismatch for date (%s) and file %s" % (str(type(date)), self.filename))

    def set_mdate(self, mdate) :
        """
        set mdate
        
        @param  mdate    mdate (a str or datetime)
        """
        self.mdate = mdate
        if not isinstance (self.mdate, datetime.datetime) :
            raise ValueError("mismatch for date (%s) and file %s" % (str(type(mdate)), self.filename))

    def set_md5(self, checksum) :
        """
        set md5
        
        @param  md5     byte
        """
        self.checksum = checksum
        if not isinstance (checksum, str) :
            raise ValueError("mismatch for checksum (%s) and file %s" % (str(type(checksum)), self.filename))

class FileTreeStatus :
    
    """
    this classes maintains a list of files
    and does some verifications in order to check if a file
    was modified or not (if yes, then it will be updated to the website)
    """
    def __init__ (self, file, fLOG = print) :
        """
        file which will contains the status
        @param      file            file, if None, fill _children
        @param      fLOG            logging function
        """
        self._file              = file
        self.copyFiles          = { }
        self.fileKeep           = file
        self.LOG                = fLOG
        
        if os.path.exists(self.fileKeep) :
            with open(self.fileKeep, "r") as f :
                for _ in f.readlines() : 
                    spl = _.strip("\r\n ").split("\t")
                    try :
                        if len(spl) >= 2 :
                            a,b  = spl[:2]
                            obj = FileInfo(a, int(b), None, None, None)
                            if len(spl) > 2 and len(spl[2]) > 0 : obj.set_date (convert_st_date_to_datetime(spl[2]))
                            if len(spl) > 3 and len(spl[3]) > 0 : obj.set_mdate (convert_st_date_to_datetime(spl[3]))
                            if len(spl) > 4 and len(spl[4]) > 0 : obj.set_md5 (spl[4])
                            self.copyFiles[a] = obj
                        else :
                            raise ValueError("expecting a filename and a date on this line: " + _)
                    except Exception as e :
                        raise Exception("issue with line:\n  {0} -- {1}".format(_, spl)) from e
            
        # contains all file to update
        self.modifiedFile = [ ]
            
    def save_dates (self, checkfile = []) :
        """
        save the status of the copy
        @param      checkfile       check the status for file checkfile
        """
        rows = []
        for k in sorted(self.copyFiles) :
            obj  = self.copyFiles[k]
            da   = "" if obj.date == None else str(obj.date)
            mda  = "" if obj.mdate == None else str(obj.mdate)
            sum5 = "" if obj.checksum == None else str(obj.checksum)

            if k in checkfile and len(da)   == 0  : raise ValueError("there should be a date for file " + k + "\n" + str(obj))
            if k in checkfile and len(mda)  == 0  : raise ValueError("there should be a mdate for file " + k + "\n" + str(obj))
            if k in checkfile and len(sum5) <= 10 : raise ValueError("there should be a checksum( for file " + k + "\n" + str(obj))
            
            values = [ k, str(obj.size), da, mda, sum5 ]
            sval   = "%s\n" % "\t".join( values)
            if "\tNone" in sval :
                raise AssertionError("this case should happen " + sval + "\n" + str(obj))
            
            rows.append ( sval )
            
        with open(self.fileKeep, "w") as f:
            for r in rows : f.write(r)
        
    def has_been_modified_and_reason (self, file) :
        """
        returns True, reason if a file was modified or False,None if not
        @param      file        filename
        @return                 True,reason or False,None
        """
        res    = True
        reason = None
        
        if file not in self.copyFiles :
            reason = "new"
            res    = True
        else :
            obj = self.copyFiles[file]
            st = os.stat(file)
            if st.st_size != obj.size :
                reason = "size %s != old size %s" % (str(st.st_size), str(obj.size))
                res    = True
            else :
                l = obj.mdate
                _m = st.st_mtime
                d = convert_st_date_to_datetime(_m)
                if d != l :
                    # dates are different but files might be the same
                    if obj.checksum != None :
                        ch = checksum_md5 (file)
                        if ch != obj.checksum :
                            reason = "date/md5 %s != old date %s  md5 %s != %s" % (str(l), str(d), obj.checksum, ch)
                            res    = True
                        else :
                            res = False
                    else :
                        # we cannot know, we do nothing
                        res = False
                else :
                    # mda.... no expected modification (dates did not change)
                    res = False
        
        if res :
            self.modifiedFile.append( (file, reason) )
        return res, reason
        
    def difference(self, files, u4 = False, nlog = None):
        """
        goes through the list of files and tells which one has changed
        
        @param      files           @see cl FileTreeNode
        @param      u4              @see cl FileTreeNode (changes the output)
        @param      nlog            if not None, print something every ``nlog`` processed files
        @return                     iterator on files which changed
        """
        memo = { }
        if u4 :
            nb = 0
            for file in files :
                memo[file.fullname] = True
                if file._file == None : continue
                nb += 1
                if nlog != None and nb % nlog == 0 :
                    self.LOG("[FileTreeStatus], processed", nb, "files")
                    
                full = file.fullname
                r, reason = self.has_been_modified_and_reason(full)
                if r :
                    if reason == "new": 
                        r = ( ">+", file._file, file, None )
                        yield r
                    else :
                        r = ( ">", file._file, file, None )
                        yield r
                else :
                    r = ( "==", file._file, file, None )
                    yield r
        else :
            nb = 0
            for file in files :
                memo[file.fullpath] = True
                nb += 1
                if nlog != None and nb % nlog == 0 :
                    self.LOG("[FileTreeStatus], processed", nb, "files")
                full = file.fullname
                if self.has_been_modified_and_reason(file):
                    yield file
                    
        for key,file in self.copyFiles.items():
            if file.filename not in memo:
                yield ( "<+", file.filename, None, None )

    def add_if_modified (self, file):
        """
        add a file to self.modifiedList if it was modified
        @param      file    filename 
        @return             True or False
        """
        res,reason = self.has_been_modified_and_reason(file)
        if res :
            memo = [ _ for _ in self.modifiedFile if _[0] == file ]
            if len(memo) == 0 :
                # not already added
                self.modifiedFile.append( (file, reason) )
        return res
        
    def update_copied_file(self, file, delete = False) :
        """
        update the file in copyFiles (before saving), update all field
        @param      file        filename
        @param      delete      to remove this file
        @return                 file object
        """
        if delete:
            if file not in self.copyFiles:
                raise FileNotFoundError("unable to find a file in the list of monitored files: {0}".format(file))
            del self.copyFiles[file]
        else :
            st      = os.stat(file)
            size    = st.st_size
            mdate   = convert_st_date_to_datetime(st.st_mtime)
            date    = datetime.datetime.now()
            md      = checksum_md5 (file)
            obj = FileInfo(file, size, date, mdate, md)
            self.copyFiles[file] = obj        
            return obj

    def copy_file (self, file, to, doClean = False, to_is_a_file = False) :
        """
        process a file copy
        @param      file            file to copy
        @param      to              destination (folder)
        @param      doClean         if True, does some cleaning before the copy 
                                    (for script in pyhome having section such as the one in tableformula.py)
        @param      to_is_a_file    it means to is a file, not a folder
        """
        if doClean :
            raise AssertionError ("this case is not meant to happen, doClean, set up at the same time")
        if len(to) == 0 :
            raise ValueError("an empty folder is not allowed for parameter to")
            
        folder = to
        if not os.path.exists (folder) :
            ffff, last = os.path.split(to)
            if to_is_a_file :
                folder = ffff
            elif "." in last :
                raise ValueError("are you sure to is not a file :" + to + "?")
            
            if not os.path.exists (folder) :
                self.LOG("creating folder ", folder)
                os.makedirs (folder)
                
            try :    
                shutil.copy (file, to)
                if not os.path.isfile(to) :
                    to = os.path.join (to, os.path.split(file)[-1] )
                self.LOG("+ copy ", file, " as ", to)
            except Exception as e :
                self.LOG ("issue with ", file, " copied to ", to)
                self.LOG ("error message: ", e)
                
            return to
                        
    def copy_file_ext (self, file, exte, to, doClean = False) :
        """
        @see me copy_file
        """
        fi = os.listdir (file)
        for f in fi :
            if not os.path.isfile (file + "/" + f) : continue
            ro, ext = os.path.splitext (f)
            if exte == None or ext [1:] == exte :
                self.copy_file (file + "/" + f, to, doClean)
        
    def copy_file_contains (self, file, pattern, to, doClean = False) :
        """
        @see me copy_file
        """
        fi = os.listdir (file)
        for f in fi :
            if not os.path.isfile (file + "/" + f) : continue
            if pattern in f :
                self.copy_file (file + "/" + f, to, doClean)
                