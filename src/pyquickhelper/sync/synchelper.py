# coding: latin-1
"""
@file

@brief Series of functions related to folder, explore, zip, gzip, synchronize, remove (recursively).
"""

import os, re, zipfile, datetime, gzip

from ..loghelper.flog           import fLOG
from .file_tree_node            import FileTreeNode
from .file_tree_status          import FileTreeStatus

def explore_folder (folder, pattern = None, fullname = False) :
    """returns the list of files included in a folder and in the subfolder
    @param          folder      (str) folder
    @param          pattern     (str) if None, get all files, otherwise, it is a regular expression, 
                                the filename must verify (with the folder is fullname is True)
    @param          fullname    (bool) if True, include the subfolder while checking the regex (pattern)
    @return                     a list of folders, a list of files (the folder is not included the path name)
    """
    if pattern != None :
        pattern = re.compile (pattern)
    
    file, rep = [], { }
    for r, d, f in os.walk (folder) :
        for a in f : 
            temp = os.path.join (r, a)
            if pattern != None :
                if fullname :
                    if not pattern.search (temp) : continue
                else :
                    if not pattern.search (a) : continue
            file.append (temp)
            r = os.path.split (temp) [0]
            rep [r] = None
            
    keys = list(rep.keys ())
    keys.sort ()
    return keys, file
    
def explore_folder_iterfile (folder, pattern = None, fullname = False) :
    """iterator of the list of files... 
    included in a folder and in the subfolder
    @param          folder      folder
    @param          pattern     if None, get all files, otherwise, it is a regular expression, 
                                the filename must verify (with the folder is fullname is True)
    @param          fullname    if True, include the subfolder while checking the regex
    @return                     a list of folders, a list of files (the folder is not included the path name)
    """
    if pattern != None :
        pattern = re.compile (pattern)
    
    file, rep = [], { }
    for r, d, f in os.walk (folder) :
        for a in f : 
            temp = os.path.join (r, a)
            if pattern != None :
                if fullname :
                    if not pattern.search (temp) : continue
                else :
                    if not pattern.search (a) : continue
            #file.append (temp)
            yield temp
            r = os.path.split (temp) [0]
            rep [r] = None
            
def explore_folder_iterfile_repo (folder, log = fLOG) :
    """
    returns all files present in folder and added to svn
    @param      folder      folder
    @param      log         log function
    @return                 iterator
    """
    node = FileTreeNode (folder, repository = True, log = log)
    svnfiles = node.get_dict ()
    for file in svnfiles :
        yield file
            
def zip_files (filename, fileSet, log = fLOG) :
    """
    put all files from an iterator in a zip file
    @param      filename        final zip file
    @param      fileSet         iterator on file to add
    @param      log             log function
    @return                     number of added files
    """
    nb = 0
    a1980 = datetime.datetime(1980,1,1)
    with zipfile.ZipFile(filename, 'w') as myzip:
        for file in fileSet :
            st    = os.stat(file)
            atime = datetime.datetime.fromtimestamp(st.st_atime)
            mtime = datetime.datetime.fromtimestamp(st.st_mtime)
            if atime < a1980 or mtime < a1980 :
                new_mtime = st.st_mtime + (4*3600) #new modification time
                while datetime.datetime.fromtimestamp(new_mtime) < a1980 :
                    new_mtime = new_mtime + (4*3600) #new modification time
                
                log("zip_files: changing time timestamp for file ", file)
                os.utime(file,(st.st_atime,new_mtime))
                
            myzip.write(file)
            nb += 1
    return nb
                
def gzip_files (filename_gz, fileSet, log = fLOG, filename_zip = None) :
    """
    put all files from an iterator in a zip file and then in a gzip file
    @param      filename_gz     final gzip file (double compression, extension should something like .zip.gz)
    @param      filename_zip    temporary zip file (will be removed after the zipping unless it is different from None)
    @param      fileSet         iterator on file to add
    @param      log             log function
    @return                     number of added files
    """
    if filename_zip == None :
        zipf = filename_gz + ".temp.zip"
    else : zipf = filename_zip
    nb = zip_files (zipf, fileSet, log = log)
    
    f = gzip.open(filename_gz, 'wb')
    with open(zipf, "rb") as gr :
        bb = gr.read(1000000)
        while len(bb) > 0 :
            f.write(bb)
            bb = gr.read(1000000)
    f.close()
    
    if filename_zip == None :
        os.remove (zipf)
    
    return nb
    
def synchronize_folder (   p1, 
                    p2, 
                    hash_size       = 1024**2, 
                    repo1           = False, 
                    repo2           = False, 
                    size_different  = True,
                    no_deletion     = False,
                    filter          = None,
                    filter_copy     = None,
                    avoid_copy      = False,
                    operations      = None,
                    file_date       = None,
                    log1            = False) :
    """
    synchronize two folders (or copy if the second is empty), it only copies more recent files.
    
    @param      p1                  (str) first path
    @param      p2                  (str) second path
    @param      hash_size           to check whether or not two files are different
    @param      repo1               assuming the first folder is under SVN or GIT, it uses pysvn to get the list
                                        of files (avoiding any extra files)
    @param      repo2               assuming the second folder is under SVN or GIT, it uses pysvn to get the list
                                        of files (avoiding any extra files)
    @param      size_different      if True, a file will be copied only if size are different,
                                    otherwise, it will be copied if the first file is more recent
    @param      no_deletion         if a file is found in the second folder and not in the first one,
                                    if will be removed unless no_deletion is True
    @param      filter              (str) None to accept every file, a string if it is a regular expression, 
                                    a function for something more complex: function (fullname) --> True (every file is considered in lower case),
                                    (use Regex.search and not Regex.match)
    @param      filter_copy         (str) None to accept every file, a string if it is a regular expression, 
                                    a function for something more complex: function (fullname) --> True
    @param      avoid_copy          if True, just return the list of files which should be copied but does not do the copy
    @param      operations          if None, this function is called with the following parameters: ``operations(op,n1,n2)``,
                                    if should return True if the file was updated
    @param      file_date           filename which contains information about when the last sync was done
    @param      log1                @see cl FileTreeNode
    @return                         list of operations done by the function
                                        list of 3-uple: action, source_file, dest_file
                                        
    if ``file_date`` is mentioned, the second folder is not explored. Only
    the modified files will be taken into account (except for the first sync).
    
    @example(synchronize two folders)
    The following function synchronizes a folder with another one
    on a USB drive or a network drive. To minimize the number of access
    to the other location, it stores the status of the previous 
    synchronization in a file (``status_copy.txt`` in the below example).
    Next time, the function goes through the directory and sub-directories
    to synchronize and only propagates the modifications which happened
    since the last modification.
    The function ``filter_copy`` defines what file to synchronize or not.
    @code
    def filter_copy(file):
        return "_don_t_synchornize_" not in file    
    
    synchronize_folder( "c:/mydata",
                        "g:/mybackup",
                        hash_size = 0,
                        filter_copy = filter_copy,
                        file_date = "c:/status_copy.txt")    
    @endcode
    
    The function is able to go through 90.000 files and 90 Gb
    in 12 minutes (for an update).
    @endexample
    """
    
    fLOG ("form ", p1)
    fLOG ("to   ", p2)
    
    if file_date != None and not os.path.exists(file_date):
        with open(file_date,"w") as f : f.write("")
    
    if filter == None :
        tfilter = lambda v : True 
    elif isinstance(filter,str) : 
        exp = re.compile (filter)
        tfilter = lambda be : (True if exp.search (be) else False)
    else :
        tfilter = filter
    
    def pr_filter (root, path, f, d) :
        if d : return True
        root = root.lower ()
        path = path.lower ()
        f    = f.lower ()
        be   = os.path.join (path, f)
        return tfilter (be)
        
    if isinstance(filter_copy,str):
        rg = re.compile(filter_copy)
        filter_copy = lambda f, ex=rg : rg.search(file) != None
        
    f1  = p1
    f2  = p2
    
    fLOG ("   exploring ", f1)
    node1 = FileTreeNode (f1, filter = pr_filter, repository = repo1, log = True, log1 = log1)
    fLOG ("     number of found files (p1)", len (node1), node1.max_date ())
    if file_date != None :
        log1n = 1000 if log1  else None
        status = FileTreeStatus(file_date, fLOG = fLOG)
        res = list(status.difference(node1, u4=True, nlog = log1n))
    else :
        fLOG ("   exploring ", f2)
        node2 = FileTreeNode (f2, filter = pr_filter, repository = repo2, log = True, log1 = log1)
        fLOG ("     number of found files (p2)", len (node2), node2.max_date ())
        res = node1.difference (node2, hash_size = hash_size)
        status = None
        
    action = [ ]
    modif = 0
    
    for op, file, n1, n2 in res :

        if filter_copy != None and not filter_copy(file) :
            continue 
            
        if operations != None :
            r = operations(op,n1,n2)
            if r and status != None : 
                status.update_copied_file (n1.fullname)
                modif += 1
                if modif % 50 == 0 : status.save_dates()
        else :
                
            if op in [">", ">+"] :
                if not n1.isdir () : 
                    if file_date != None or not size_different or n2 == None or n1._size != n2._size :
                        if not avoid_copy : n1.copyTo (f2)
                        action.append ( (">+", n1, f2) )
                        if status != None : 
                            status.update_copied_file (n1.fullname)
                            modif += 1
                            if modif % 50 == 0 : status.save_dates()
                    else :
                        pass
                        
            elif op in ["<+"] :
                if n2 == None :
                    if not no_deletion: 
                        # this case happens when we do not know sideB (sideA is stored in a file)
                        # we need to remove file, file refers to this side
                        filerel = os.path.relpath(file, start=p1)
                        filerem = os.path.join(p2, filerel)
                        action.append ( (">-", None, FileTreeNode(p2, filerel) ) )
                        if not avoid_copy : 
                            fLOG ("- remove ", filerem)
                            os.remove(filerem)
                        if status != None : 
                            status.update_copied_file (file, delete = True)
                            modif += 1
                            if modif % 50 == 0 : status.save_dates()
                else :
                    if not n2.isdir () and not no_deletion: 
                        if not avoid_copy : n2.remove ()
                        action.append ( (">-", None, n2) )
                        if status != None : 
                            status.update_copied_file (n1.fullname, delete = True)
                            modif += 1
                            if modif % 50 == 0 : status.save_dates()
            elif n2 != None and n1._size != n2._size and not n1.isdir () :
                fLOG ("problem", "size are different for file %s (%d != %d) dates (%s,%s) (op %s)" % (file, n1._size, n2._size, n1._date, n2._date, op))
                #n1.copyTo (f2)
                #raise Exception ("size are different for file %s (%d != %d) (op %s)" % (file, n1._size, n2._size, op))    
                
    if status != None :
        status.save_dates(file_date)
    
    return action

def remove_folder (top, remove_also_top = True) :
    """
    remove everyting in folder top
    @param      top                 path to remove
    @param      remove_also_top     remove also root
    @return                         list of removed files and folders
                                     --> list of tuple ( (name, "file" or "dir") )
    """
    if top in ["", "C:", "c:", "C:\\", "c:\\", "d:", "D:", "D:\\", "d:\\" ] :
        raise Exception("top is a root (c: for example), this is not safe")
    
    res = [ ]
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            t = os.path.join(root, name)
            os.remove(t)
            res.append((t,"file"))
        for name in dirs:
            t = os.path.join(root, name)
            os.rmdir(t)    
            res.append ( (t,"dir") )
            
    if remove_also_top :
        res.append ( (root,"dir") )
        os.rmdir(root)
            
    return res
