"""
@file
@brief To format a pandas dataframe
"""

def df_to_rst(df, add_line=True):
    """
    builds a string in RST format from a dataframe
    @param      df              dataframe
    @param      add_line        (bool) add a line separator between each row
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
    length = [ _+ 2 for _ in length ]
    line   = [ "-" * l for l in length ]
    lineb  = [ "=" * l for l in length ]
    sline  = "+%s+" % ("+".join(line))
    slineb = "+%s+" % ("+".join(lineb))
    res    = [ sline ]
    
    def complete(cool) :
        s,i = cool
        s = str(s)
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
    return "\n".join(res) + "\n"
    
    
