import io

def get_dynasties(file,cur):
    # The following code adds in-game dynasties to the game
    # read until we hit the dynasties
    line = file.readline()
    done = False
    while(not done):
        line = file.readline()
        #beginning of dynasties data
        if line=='\tdynasties=\n':
            line = file.readline() #get rid of '\t{\n'
            line = file.readline()
            #while not the end of the data '\t}\n'
            while line!='\t}\n':
                #parse this dynasty
                line = line.strip()
                #get the id
                i = line[0:len(line)-1]
                #get the name
                line = file.readline()
                line = file.readline()
                #historical dynasties are missing information: name appears as f_arms
                name = None         
                cul = None
                rel = None
                if 'name' in line:
                    #difficulties in finding and removing " symbols as well as comments (denoted by #)
                    #  :(
                    index = line.find('"')
                    if index==-1:
                        index = line.find('=')
                    name = line[index+1:]
                    name = name.strip()                    
                    name = name.strip('"')
                    name = name.rstrip('"')
                    name = name.strip()
                    index = name.find('"')
                    if index!=-1:
                        name = name[0:index-1]
                    index = name.find('#')
                    if index!=-1:
                        name = name[0:index-2]
                    #next two lines are culture and religion
                    line = file.readline()
                    cul = line.split('=')[1]
                    cul = cul.strip()
                    cul = cul.strip('"')
                    cur.execute('SELECT cultureID FROM culture WHERE cultureName=%s',[cul])
                    cul = cur.fetchone()[0]
                    line = file.readline()
                    rel = line.split('=')[1]
                    rel = rel.strip()
                    rel = rel.strip('"')
                    cur.execute('SELECT religionID FROM religion WHERE religionName=%s',[rel])
                    rel = cur.fetchone()[0]
                #add to the database
                cur.execute('INSERT INTO dynasty Values(%s,%s,%s,%s)',[i,name,cul,rel])
                #ignore the next lines until end of dynasty
                while(line!='\t\t}\n'):
                    line = file.readline()
                # the next line is either a new dynasty or the end of the file
                line = file.readline()
            done = True
    
    # add information for existant historical dynasties
    with io.open('00_dynasties.txt',encoding="cp1252") as f:
        line = f.readline()
        while(line!='}'):
            #line is currently an id
            index = line.find('=')
            i = line[0:index]
            #get missing name   
            while(line[1:5]!='name'):
                line = f.readline()
            index = line.find('"')
            if index==-1:
                index = line.find('=')
            name = line[index+1:]
            name = name.strip()
            name = name.strip('"')
            name = name.rstrip('"')
            name = name.strip()
            index = name.find('"')
            if index!=-1:
                name = name[0:index-1]
            index = name.find('#')
            if index!=-1:
                name = name[0:index-2]                
            #move until end of parse block
            while(line!='}\n' and line!='}'):
                line = f.readline()
            #add the name to the table
            cur.execute('UPDATE dynasty SET dynastyName = %s WHERE dynastyID=%s',[name,i])
            #move pointer to next integer entry
            line = f.readline()
            #end of file when nextline is nothing
            if len(line)==0:
                break
            #ignore whitespace
            while line=='\n' or line[0]=='#':
                line = f.readline()
            