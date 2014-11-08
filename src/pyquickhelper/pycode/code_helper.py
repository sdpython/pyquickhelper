"""
@file
@brief Various function to clean the code.
"""

def remove_extra_spaces(filename):
    """
    removes extra spaces in a filename, replace the file in place
    
    @param      filename        file name
    @return                     number of removed extra spaces
    """
    with open(filename, "r") as f :
        lines = f.readlines()
    
    lines2 = [ _.rstrip(" \r\n") for _ in lines ]
    
    diff = len("".join(lines)) - len("\n".join(lines2))
    if diff != 0:
        with open(filename,"w") as f :
            f.write("\n".join(lines2))
    return diff
    