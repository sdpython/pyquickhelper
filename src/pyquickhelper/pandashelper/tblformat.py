"""
@file
@brief To format a pandas dataframe
"""

def df_to_rst(df, add_line=True, align = None):
    """
    builds a string in RST format from a dataframe
    @param      df              dataframe
    @param      add_line        (bool) add a line separator between each row
    @param      align           a string (l,r,c,p{5cm}) or a list of the same
    @return                     string

    It produces the following results:
    
    @code
    +------------------------+------------+----------+----------+
    | Header row, column 1   | Header 2   | Header 3 | Header 4 |
    | (header rows optional) |            |          |          |
    +========================+============+==========+==========+
    | body row 1, column 1   | column 2   | column 3 | column 4 |
    +------------------------+------------+----------+----------+
    | body row 2             | ...        | ...      |          |
    +------------------------+------------+----------+----------+        
    @endcode
    """
    length  = [ len(_) for _ in df.columns ]
    for row in df.values :
        for i,v in enumerate(row) :
                length[i] = max ( length[i], len(str(v)) )

    ic = 3
    length = [ _+ ic for _ in length ]
    line   = [ "-" * l for l in length ]
    lineb  = [ "=" * l for l in length ]
    sline  = "+%s+" % ("+".join(line))
    slineb = "+%s+" % ("+".join(lineb))
    res    = [ sline ]
    
    def complete(cool) :
        s,i = cool
        s = str(s) + " "
        i -= 2
        if len(s) < i : s += " " * (i-len(s))
        return s
    
    res.append ( "| %s |" % " | ".join (map (complete, zip(df.columns, length)) ) )
    res.append (slineb)
    res.extend ( [ "| %s |" % " | ".join ( map(complete, zip(row,length) )) for row in df.values ] )
    if add_line :
        t = len(res)
        for i in range(t-1,3,-1) : 
            res.insert(i, sline)
    res.append (sline)
    table = "\n".join(res) + "\n"
    
    if align != None :
        if isinstance(align,str):
            align = ("|" + align) * len(length) + "|"
        elif isinstance(align,list):
            align = "|%s|" % "|".join(align)
        else :
            raise TypeError(str(type(align)))
        align = ".. tabularcolumns:: " + align + "\n\n"
        return align + table
    else :
        return table
    
def df_to_html (self, class_table = None, class_td = None, class_tr = None, class_th = None) :
    """
    convert the table into a html string
    
    @param  class_table     adds a class to the tag ``table`` (None for none)
    @param  class_td        adds a class to the tag ``td`` (None for none)
    @param  class_tr        adds a class to the tag ``tr`` (None for none)
    @param  class_th        adds a class to the tag ``th`` (None for none)
    """
    clta = ' class="%s"' % class_table  if class_table != None else ""
    cltr = ' class="%s"' % class_tr     if class_tr != None else ""
    cltd = ' class="%s"' % class_td     if class_td != None else ""
    clth = ' class="%s"' % class_th     if class_th != None else ""
    
    rows= [ "<table%s>" % clta ]
    rows.append (  ("<tr%s><th%s>" % (cltr, clth)) + ("</th><th%s>" % clth).join (self.columns) + "</th></tr>" )
    septd = "</td><td%s>" % cltd
    strtd = "<tr%s><td%s>" % (cltr, cltd)
    for row in self.values :
        s = septd.join ( [ str(_) for _ in row ] )
        rows.append ( strtd + s + "</td></tr>")
    rows.append ("</table>")
    rows.append("")
    return "\n".join(rows)
    

