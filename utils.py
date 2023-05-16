import json

def read_file(file_name,extension):
    """Read the given file
    -----------------------------
    Input params: 
    -----------------------------
    file_name: str
    Name of the file without extension

    extension: str
    extension of the file eg: json, txt 

    Output params:
    -----------------------------
    op: json / str
    """
    if extension == "json":
        with open(f"{file_name}.json","r") as t:
            op = json.load(t)
    elif extension == "txt":
        with open(f"{file_name}.txt","r") as n:
            op = n.readlines()
    return op

def write_file(file,file_name,extension):
    """Write the given file to gven extension
    -----------------------------
    Input params:
    -----------------------------
    file: dictionary / str
    File to be written to given extension

    file_name: str
    Name of the file without extension

    extension: str
    extension of the file eg: json, txt 
    """
    if extension == "json":
        with open(f"{file_name}.json", "w") as outfile:
            json.dump(file, outfile)
    elif extension == "txt":
        with open(f"{file_name}.txt","w") as n:
            n.write(file)


def get_unique_from_ls(ls_ls):
    """
    Return the unique elements from the given list of lists
    -----------------------
    Input params: 

    ls_ls: list
    List of lists with duplicate elements in the degenerate lists

    Output params:
    -----------------------------
    op: list
    list with unique elements
    """
    op = list(set(ls_ls))
    return op



