#-*- coding: utf-8 -*-
"""
@file
@brief  various basic functions often needed
"""

import math, os, re, random, time, sys

from ..loghelper.flog import fLOG, GetSepLine
from ..sync.synchelper import explore_folder_iterfile



_keep_var_character = re.compile ("[^a-zA-Z0-9_]")

def _clean_name_variable (st) :
    """clean a string
    @param      st      string to clean
    @return             another string
    """
    res = _keep_var_character.split (st)
    if res is None :
        raise Exception ("unable to clean " + st)
    return "_".join (res)

def _get_format_zero_nb_integer (nb) :
    h = nb
    c = 0
    while h > 0 : 
        h = int (h/10)
        c += 1
    if c > 20 :
        raise Exception("this should not be that high %s (nb=%s)" % (str(c), str(nb)))
    return "%0" + str (int(c)) + "d"

def test_regular_expression (   exp     = ".*", 
                                text    = "") :
    """
    test a regular expression
    @param      exp     regular expression
    @param      text    text to check
    """
    fLOG ("regex", exp)
    fLOG ("text", text)
    ex = re.compile (exp)
    ma = ex.search (text)
    if ma is None : fLOG ("no result")
    else : fLOG (ma.groups ())

def IsEmptyString(s):
    """
    tells if a string is empty

    @param      s       string
    @return             boolean
    """
    if s is None: return True
    return len(s) == 0
    
def file_head ( file = "",
                head = 1000,
                out  = "") :
    """
    keep the head of a file
    
    @param      file        file name
    @param      head        number of lines to keep
    @param      out         output file, if == None or empty, then, it becomes:
                                file + ".head.%d.ext" % head
    @return                 out
    """
    if not os.path.exists (file) :
        raise Exception ("unable to find file %s" % file)
    if IsEmptyString (out) :
        f, ext = os.path.splitext (file)
        out = "%s.head.%d%s" % (file, head, ext)
        
    f = open (file, "r")
    g = open (out, "w")
    for i,line in enumerate (f) :
        if i >= head : break
        g.write (line)
    f.close ()
    g.close ()
    return out
        
def file_split (file   = "",
                nb     = 2,
                out    = "",
                header = False,
                rnd    = False) :
    """
    keep the head of a file
    
    @param      file        file name
    @param      nb          number of files
    @param      out         output file, if == None or empty, then, it becomes:
                                file + ".split.%d.ext" % head
    @param      header      consider a header or not
    @param      rnd         randomly draw the file which receives the current line
    """
    if not os.path.exists (file) :
        raise Exception ("unable to find file %s" % file)
        
    if IsEmptyString (out) : 
        f, ext = os.path.splitext (file)
        out = "%s.split.%s%s" % (file, _get_format_zero_nb_integer (nb), ext)
        
    size = os.stat (file).st_size
    f    = open (file, "r")
    g    = { }
    tot  = 0
    for i,line in enumerate (f) :
        if i == 0 and header :
            for n in range (0, nb) :
                if n not in g : g [n] = open (out % n, "w")
                g [n].write (line)
            continue

        if rnd : 
            n = random.randint (0, nb-1)
        else : 
            n = int(min (nb, tot * nb / size))
            tot += len (line)
        
        if n not in g : g [n] = open (out % n, "w")
        g [n].write (line)
        
        if (i+1) % 10000 == 0 :
            fLOG ("    processed ", i, " bytes ", tot, " out of ", size, " lines in ", out)
        
    f.close ()
    for k,v in g.items () :
        v.close ()
        
def file_list (file, out = "") :
    """
    prints the list of files and sub files in a text file
    
    @param      file        folder
    @param      out         result
    @return                 out
    """
    
    if IsEmptyString (out) :
        f, ext = os.path.splitext (file)
        out = "%s_.list_of_files.txt" % (file)

    f = open (out, "w")
    for l in explore_folder_iterfile (file) :
        f.write (l)
        f.write (GetSepLine())
    f.close ()
    
    return out

def file_grep ( file = "",
                regex = ".*",
                out  = "",
                head = 100) :
    """
    grep
    
    @param      file        file name
    @param      regex        regular expression
    @param      out         output file, if == None or empty, then, it becomes:
                                file + ".head.%d.ext" % head
    @param      head        head
    @return                 out
    """
    if not os.path.exists (file) :
        raise Exception ("unable to find file %s" % file)
    if IsEmptyString (out) :
        f, ext = os.path.splitext (file)
        out = "%s.regex.%d%s" % (file, head, ext)
        
    exp = re.compile (regex)
        
    f = open (file, "r")
    g = open (out, "w")
    for i,line in enumerate (f) :
        if exp.search (line) :
            g.write (line)
    f.close ()
    g.close ()
    return out
        
