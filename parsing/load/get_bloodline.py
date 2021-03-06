def get_bloodlines(data, cur):
    for bloodlineID in data:
        obj = data[bloodlineID]
        cur.execute('INSERT INTO BloodLines Values(?, ?, ?)',
            [bloodlineID, data.get('type'), data.get('owner')]
        )
        members = obj.get('member')
        if not isinstance(members, list):
            members = [members]
        for memberID in members:
            cur.execute('INSERT INTO BloodLineMembers Values(?,?)', [memberID, bloodlineID])
