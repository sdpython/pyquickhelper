"""
@file
@brief various variables and classes used to produce a Sphinx documentation

"""

import inspect, os, copy, re, sys
from pandas import DataFrame
from ..pandashelper.tblformat import df_to_rst

class HelpGenException(Exception):
    """
    custom exception
    """
    pass

_length_truncated_doc = 120


    
add_file_rst_template = """
__FULLNAME_UNDERLINED__


.. module:: __FULLNAMENOEXT__
  :synopsis: __DOCUMENTATIONLINE__
  :platform: __PLATFORM__
  

Short summary
+++++++++++++
      
__DOCUMENTATION__
   

__CLASSES__

__FUNCTIONS__

__PROPERTIES__

__STATICMETHODS__

__METHODS__

Documentation
+++++++++++++

.. automodule:: __FULLNAMENOEXT__
    :members:
    :show-inheritance:
__ADDEDMEMBERS__

"""

add_file_rst_template_cor = { "class":"__CLASSES__", 
                              "method":"__METHODS__",
                              "function":"__FUNCTIONS__",
                              "staticmethod":"__STATICMETHODS__",
                              "property":"__PROPERTIES__",
                              }

add_file_rst_template_title = { "class":"Classes", 
                                "method":"Methods",
                                "function":"Functions",
                                "staticmethod":"Static Methods",
                                "property":"Properties",
                                }

#
#:platform: Unix, Windows
#   :synopsis: Analyze and reanimate dead parrots.
#.. moduleauthor:: Eric Cleese <eric@python.invalid>
#.. moduleauthor:: John Idle <john@python.invalid>
#  for autosummary
#   :toctree: __FILENAMENOEXT__/
#

def compute_truncated_documentation(doc, 
                                    length = _length_truncated_doc,
                                    raise_exception = False):
    """
    produces a truncated version of a docstring
    @param      doc                 doc string
    @param      length              approximative length of the truncated docstring
    @param      raise_exception     raises an exception when the result is empty and the input is not
    @return                         truncated doc string
    """
    if len(doc) == 0 :
        return doc
    else :
        doc_ = doc
        
        if "@brief " in doc :
            doc = doc.split("@brief ")
            doc = doc[-1]
            
        doc = doc.strip("\n\r\t ")
        doc = doc.replace("\n", " ").replace("\r", "").strip("\n\r\t ")
        
        for subs in ["@" + "param", "@" + "return", ":param", ":return" ] :
            if subs in doc :
                doc = doc[:doc.find(subs)].strip("\r\t ")
                
        if len(doc) >= _length_truncated_doc :
            spl = doc.split(" ")
            doc = ""
            cq  = 0
            i   = 0
            while len(doc) < _length_truncated_doc or cq % 2 != 0:
                cq  += spl[i].count("`")
                doc += spl[i] + " "
                i   += 1
            doc += "..."
        
        if raise_exception and len(doc) == 0 :
            raise ValueError("bad format for docstring: " + doc_)
        return doc
        
class ModuleMemberDoc :
    """
    represents a member in a module
    
    @var    obj         object
    @var    type        (str) type
    @var    cl          (class) class it belongs to
    @var    name        (str)
    @var    module      (module)
    @var    doc         (str) documentation
    @var    truncdoc    (str) truncated documentation    
    """
    def __init__ (self, obj, ty = None, cl = None, name = None) :
        """
        constructor
        @param      obj     anykind of object
        @param      ty      type (if you want to overwrite what the class will choose),
                            this type is a string (class, method, function)
        @param      cl      if is a method, class it belongs to
        """
        self.obj = obj
        self.cl  = cl
        if ty != None : self.type = ty
        self.name = name
        self.populate()
        
        if self.cl == None and self.type in [ "method", "staticmethod", "property" ] :
            self.cl = self.obj.__class__
        if self.cl == None and self.type in [ "method", "staticmethod", "property" ] :
            raise TypeError("N/a method must have a class (not None): %s" % str(self.obj))
            
    def add_prefix(self, prefix) :
        """
        adds a prefix (for the documentation)
        @param      prefix      string
        """
        self.prefix = prefix
            
    @property
    def key (self) :
        """
        returns a key to identify it
        """
        return "%s;%s" % (self.type, self.name)
        
    def populate(self) :
        """
        extract some information about an object
        """
        obj = self.obj
        ty  = self.type if "type" in self.__dict__ else None
        if ty == None :
            if inspect.isclass (obj) :
                self.type = "class"
            elif inspect.ismethod (obj) :
                self.type = "method"
            elif inspect.isfunction(obj) :
                self.type = "function"
            else :
                raise TypeError ("E/unable to deal with this type: " + str(type(obj)))
                
        if ty == "method":
            if isinstance(obj, staticmethod):
                self.type = "staticmethod"
            elif isinstance(obj, property):
                self.type = "property"
            
        # module
        try :
            self.module = obj.__module__
            self.name   = obj.__name__
        except Exception :
            if self.type in ["property", "staticmethod"]:
                self.module = self.cl.__module__
            else :
                self.module = None
            if self.name == None : raise IndexError("unable to find a name for this object")
            
        # documentation
        if self.type == "staticmethod" :
            try :
                self.doc = obj.__func__.__doc__
            except Exception as ie :
                self.doc = str(ie) + " \n----------\n " + str(dir(obj))
        else :
            try :
                self.doc = obj.__doc__
            except Exception as ie :
                self.doc = str(ie) + " \n----------\n " + str(dir(obj))
        
        try :    self.file   = self.module.__file__
        except : self.file = ""

        # truncated documentation
        if self.doc != None :
            self.truncdoc = compute_truncated_documentation(self.doc)
        else :
            self.doc = ""
            self.truncdoc = ""
            
        if self.name == None :
            raise TypeError("S/name is None for object: %s" % str(self.obj))
        
    def __str__(self) :
        """
        usual
        """
        clname = ".%s" % self.cl.__name__ if self.cl != None else ""
        mes = "%s in %s%s: %s (%s)" % (self.type, self.module, clname, self.name, self.truncdoc)
        return mes
        
    def rst_link(self, prefix = None, class_in_bracket = True) :
        """
        returns a sphinx link on the object
        @param      prefix              to correct the path with a prefix
        @param      class_in_bracket    if True, adds the class in bracket for methods and properties
        @return                         a string style::
        
                                            :%s:`%s <%s>`               or
                                            :%s:`%s <%s>` (class)
        """
        cor = {"function":"func", "method":"meth", 
                "staticmethod":"meth", "property":"meth" }
        
        if prefix == None and "prefix" in self.__dict__ :
            prefix = self.prefix
        
        if self.type in ["method", "staticmethod", "property"]:
            path = "%s.%s.%s" % (self.module, self.cl.__name__, self.name)
        else :
            path = "%s.%s" % (self.module, self.name)
            
        if prefix != None :
            path = "%s.%s" % (prefix, path)
        
        if self.type in ["method", "staticmethod", "property"] and class_in_bracket :
            link = ":%s:`%s <%s>` (%s)" % (cor.get(self.type, self.type), self.name, path, self.cl.__name__)
        else :
            link = ":%s:`%s <%s>`" % (cor.get(self.type, self.type), self.name, path)
        return link
        
    @property
    def classname (self):
        """
        returns the class name if the object is a method
        @return     class object
        """
        if self.type in ["method", "staticmethod", "property"] :
            return self.cl
        else :
            return None
        
    def __cmp__ (self, oth) :
        """
        comparison operators, compares first the first, second the name (lower case)
        @param      oth         other object
        @return                 -1, 0 or 1
        """
        if self.type == oth.type :
            ln = self.name.lower()
            lo = oth.name.lower()
            c  = -1 if ln < lo else (1 if ln > lo else 0)
            if c == 0 and self.type == "method" :
                ln = self.cl.__name__
                lo = self.cl.__name__
                c  = -1 if ln < lo else (1 if ln > lo else 0)
            return c
        else :
            return -1 if self.type < oth.type else (1 if self.type > oth.type else 0)
            
    def __lt__(self, oth): return self.__cmp__(oth) == -1
    def __eq__(self, oth): return self.__cmp__(oth) == 0
    def __gt__(self, oth): return self.__cmp__(oth) == 1
    
class IndexInformation :
    """
    keeps some information to index
    """
    def __init__ (self, type, label, name, text, rstfile, fullname) :
        """
        @param      type        each type gets an index
        @param      label       label used to index
        @param      name        name to display
        @param      text        text to show as a short description
        @param      rstfile     tells which file the index refers to (rst file)
        @param      fullname    fullname of a file the rst file describes
        """
        self.type = type
        self.label = label
        self.name = name
        self.text = text
        self.fullname = fullname
        self.set_rst_file(rstfile)
        
    def __str__(self):
        """
        usual
        """
        return "%s -- %s" % (self.label, self.rst_link())
        
    def set_rst_file(self, rstfile) :
        """
        sets the rst file and checks the label is present in it
        @param      rst_file        rst_file
        """
        self.rstfile = rstfile
        if rstfile != None :
            self.add_label_if_not_present()
        
    @property
    def truncdoc (self):
        """
        returns self.text
        """
        return self.text.replace("\n", "  ").replace("\t","").replace("\r","")
    
    def add_label_if_not_present(self):
        """
        The function checks the label is present in the original file.
        """
        if self.rstfile != None :
            with open(self.rstfile,"r",encoding="utf8") as f : 
                content = f.read()
            label = ".. _%s:" % self.label
            if label not in content :
                content = "\n%s\n%s" % (label, content)
                with open(self.rstfile,"w",encoding="utf8") as f : 
                    f.write(content)
        
    def get_label(existing, suggestion) :
        """
        returns a new label given the existing ones
        @param  existing    existing labels stored in a dictionary
        @param  suggestion  the suggestion will be chosen if it does not exists, ``suggestion + zzz`` otherwise
        @return             string
        """
        suggestion = suggestion.replace("_","").replace(".","")
        while suggestion in existing :
            suggestion += "z"
        return suggestion
    get_label = staticmethod(get_label)
    
    def rst_link(self) :
        """
        return a link rst
        @return     rst link
        """
        if self.label.startswith("_") :
            return ":ref:`%s`" % self.label[1:]
        else :
            return ":ref:`%s`" % self.label
    
class RstFileHelp :
    """
    defines what a rst file and what it describes
    """
    def __init__ (self, file, rst, doc) :
        """
        @param      file        original filename
        @param      rst         produced rst file
        @param      doc         documentation if any
        """
        self.file = file
        self.rst  = rst
        self.doc  = doc

def import_module (filename, log_function, additional_sys_path = [ ]) :
    """
    import a module using its filename
    @param      filename                file name of the module
    @param      log_function            logging function
    @param      additional_sys_path     additional path to include to sys.path before importing a module (will be removed afterwards)
    @return                             module object
    
    @warning It adds the file path at the first position in sys.path and then deletes it.
    """
    memo = copy.deepcopy(sys.path)
    l = filename
    sdir = os.path.abspath(os.path.split (l) [0])
    sys.path.insert (0, sdir)
    tl  = os.path.split (l) [1]
    fi  = tl.replace (".py", "")
    if additional_sys_path != None and len(additional_sys_path) > 0 :
        sys.path.extend(additional_sys_path)
    
    try :
        mo = __import__ (fi)
        sys.path = memo
        log_function("importing ", filename, " successfully")
        return mo
    except ImportError as e :
        exp = re.compile("No module named '(.*)'")
        find = exp.search(str(e))
        if find :
            module = find.groups()[0]
            log_function("unable to import module " + module + " --- " + str(e).replace("\n"," "))
            pass
            
        log_function("  File \"%s\", line %d" % (__file__,359))
        log_function("-- unable to import module (1) ", filename, ",", fi, " in path ", sdir, " Error: ", str(e))
        log_function("    cwd ", os.getcwd())
        log_function("    path", sdir)
        sys.path = memo
        return "unable to import %s\nError:\n%s" % (filename, str(e))
    except SystemError as e :
        log_function("-- unable to import module (2) ", filename, ",", fi, " in path ", sdir, " Error: ", str(e))
        sys.path = memo
        return "unable to import %s\nError:\n%s" % (filename, str(e))
    except Exception as e :
        log_function("-- unable to import module (3) ", filename, ",", fi, " in path ", sdir, " Error: ", str(e))
        sys.path = memo
        return "unable to import %s\nError:\n%s" % (filename, str(e))
        
def get_module_objects(mod) :
    """
    gets all the classes from a module
    @param      mod     module objects
    @return             list of ModuleMemberDoc
    """
    
    #exp = { "__class__":"",
    #        "__dict__":"",
    #        "__doc__":"",
    #        "__format__":"",
    #        "__reduce__":"",
    #        "__reduce_ex__":"",
    #        "__subclasshook__":"",
    #        "__dict__":"",
    #        "__weakref__":""
    #         }
             
    cl = [ ]
    for name, obj in inspect.getmembers(mod):
        if inspect.isclass(obj) or \
           inspect.isfunction(obj) or \
           inspect.ismethod(obj) :
            cl.append ( ModuleMemberDoc (obj) )
            if inspect.isclass(obj) :
                for n, o in inspect.getmembers(obj):
                    try :
                        ok = ModuleMemberDoc (o, "method", cl = obj, name = n)
                        if ok.module != None :
                            cl.append ( ok  )
                    except Exception as e :
                        if str(e).startswith("S/") :
                            raise e

    res = [ ]
    for _ in cl :
        try :
            #if _.module != None :
            if _.module == mod.__name__ :
                res.append(_)
        except :
            pass
            
    res.sort()
    return res
    
def process_var_tag(docstring, rst_replace = False, header = ["attribute", "meaning"]):
    """
    Process a docstring using tag ``@ var``, and return a list of 2-tuple
    
    @code
        @ var    filename        file name
        @ var    utf8            decode in utf8?
        @ var    errors          decoding in utf8 can raise some errors
    @endcode
    
    @param      docstring       string
    @param      rst_replace     if True, replace the var bloc var a rst bloc
    @param      header          header for the table
    @return                     a matrix with two columns or a string if rst_replace is True
    
    """
    
    reg = re.compile("[@]var +([_a-zA-Z][a-zA-Z0-9_]*?) +((?:(?!@var).)+)")
    
    docstring = docstring.split("\n")
    docstring = [ _.strip("\r \t") for _ in docstring ]
    docstring = [ _ if len(_) > 0 else "\n\n" for _ in docstring ]
    docstring = "\n".join(docstring)
    docstring = docstring.split("\n\n")
    
    values    = [ ]
    if rst_replace :
        for line in docstring :
            line2 = line.replace("\n", " ")
            if "@var" in line2 :
                all = reg.findall(line2)
                val = []
                for a in all :
                    val.append ( list(a) )
                if len(val)>0 :
                    tbl = DataFrame (columns=header, data=val)
                    align = ["1x"] * len(header)
                    align[-1] = "3x"
                    rst = df_to_rst(tbl, align = align)
                    values.append(rst)
            else :
                values.append (line)
        return "\n".join(values)
    else :
        for line in docstring :
            line = line.replace("\n", " ")
            if "@var" in line :
                all = reg.findall(line)
                for a in all :
                    values.append ( a )
        return values

def process_look_for_tag(tag, title, files):
    """
    looks for specific information in all files, collect them
    into one single page
    
    @param      tag     tag
    @param      title   title of the page
    @param      files   list of files to look for
    
    The function is looking for regular expression::
    
        .. tag(...).
        ...
        .. endtag.
    
    """
    repl = "__!LI!NE!__"
    exp  = re.compile("[.][.] %s[(](.*?);;(.*?)[)][.](.*?)[.][.] end%s[.]" % (tag,tag))
    exp2 = re.compile("[.][.] %s[(](.*?)[)][.](.*?)[.][.] end%s[.]" % (tag,tag))
    coll = [ ]
    for file in files :
        if file.file == None : continue
        if "utils_sphinx_doc.py" in file.file : continue
        with open(file.file,"r") as f : content = f.read()
        content = content.replace("\n",repl)
        
        all = exp.findall(content)
        all2 = exp2.findall(content)
        if len(all2) > len(all) :
            raise HelpGenException("an issue was detected in file: " + file.file)
        
        coll   += [ (a,c.replace(repl,"\n"),b) for a,b,c in all ]
    coll.sort()
    
    rows = ["""
        .. _l-{0}:

        {1}
        {2}

        .. contents::
            :depth: 3
            
        """.replace("        ","").format(tag, title, "=" * len(title))]
        
    for a,b,c in coll :
        rows.append( a )
        rows.append( "+" * len(a) )
        rows.append( "" )
        rows.append( remove_some_indent(b) )
        rows.append( "" )
        spl = c.split("-")
        d = "file {0}.py".format(spl[1]) # line, spl[2].lstrip("l"))
        rows.append( "see :ref:`%s <%s>`" % (d,c))
        rows.append( "" )

    return "\n".join(rows)
    
def remove_some_indent(s):
    """
    bring text to the left
    
    @param      s       text
    @return             text
    """
    rows = s.split("\n")
    mi = len(s)
    for l in rows :
        ll = l.lstrip()
        if len(ll) > 0 :
            d  = len(l)-len(ll)
            mi = min(d,mi)

    if mi > 0 :
        keep = [ ]
        for _ in rows :
            keep.append( _[mi:] if len(_.strip())>0 and len(_) > mi else _ )
        return "\n".join(keep)
    else :
        return s

