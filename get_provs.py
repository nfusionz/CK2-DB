import io
import re

import parser

barony_regex = {"type" : None}

province_regex = {"culture" : None,
                  "religion" : None,
                  "name" : None,
                  "._" : barony_regex}

def get_provs(file, cur):
    # Jump to beginning of provinces
    x = file.readline().strip()
    while (not x[0:len("provinces=")] == "provinces="):
        x = file.readline().strip()

    # Skip to the opening bracket
    if(not "{" in x):
        while(x and not x == "{"):
            x = file.readline().strip()
        if(not x):
            raise Exception("ERROR: No opening bracket for Provinces!")
    x = file.readline().strip()

    while(x and not x == "}"):
        if(not "=" in x):
            x = file.readline().strip()
            continue
        pair = x.split()
        try:
            id = int(x[0:-1])
        except ValueError:
            raise Exception("ERROR: Province ID is not an int!")

        province = parser.getAttr(file, province_regex, x)
        province["id"] = id

        if("name" in province): # Because we need to apply an operation on it
            province["name"] = province["name"].replace("\"","")

        # Insert the province first
        cur.execute("INSERT INTO province VALUES(%s,%s,%s,%s,%s)",
                    [province.get("id"),
                     province.get("name"),
                     None,
                     province.get("culture"),
                     province.get("religion")]
        )

        for key in province.keys():
            if(not re.match("._", key) == None):
                name = key[2].upper() + key[3:len(key)]
                cur.execute("INSERT INTO barony VALUES(%s, %s, %s)",
                            [name,
                             id,
                             province[key]["type"]])
  
        x = file.readline().strip()
            
    if(not x == "}"):
        raise Exception("ERROR: No closing bracket for Provinces!")


