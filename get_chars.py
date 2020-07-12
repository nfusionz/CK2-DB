		# Person(INT id, VARCHAR(63) birthName, INT dynasty, BOOLEAN isMale, DATE birthday, DATE deathday, INT fatherID,
		# INT real_fatherID, INT motherID, INT spouseID, INT religionID, INT cultureID, FLOAT fertility, FLOAT health, FLOAT wealth,
		# INT hostID, FLOAT prestige, FLOAT piety, INT provinceLocationID, INT employerID, INT martial, INT diplomacy, INT stewardship,
		 # INT intrigue, INT learning)

import datetime
import ck2_parser as parser

claim_title_regex = {"^title" : None}

claim_regex = {"title" : claim_title_regex,
			   "pressed" : None,
			   "weak" : None
}

person_regex = {"^bn" : None,
				"^dnt" : None,
				"^fem" : None,
				"^b_d" : None,
				"^d_d" : None,
				"^fat" : None, # The default for rfat if none specificed
				"^rfat" : None,
				"^mot" : None,
				"^spouse" : None,
				"^rel" : None,
				"^cul" : None,
				"^fer" : None,
				"^health" : None,
				"^wealth" : None,
				"^prs" : None,
				"^piety" : None,
				"^emp" : None,
				"^host" : None,
				"^oh" : None,
				"^att" : None, # This needs to be broken up manually
				"^tr" : None, # This needs to be broken up manually
				"^claim" : claim_regex # Repeated
}

def make_person_attributes(att):
	attr_list = att[1:-1].strip().split() # Remove brackets
	attributes = {"diplomacy" : int(attr_list[0]),
				  "martial" : int(attr_list[1]),
				  "steward" : int(attr_list[2]),
				  "intrigue" : int(attr_list[3]),
				  "learning" : int(attr_list[4])
	}
	return attributes

def make_traits(tr):
	return tr[1:-1].strip().split()

def make_date(str):
	dt_arr = str.split('.')
	year = int(dt_arr[0])
	month = int(dt_arr[1])
	day = int(dt_arr[2])

	result_date = datetime.date(year, month, day)
	return result_date

def get_cul_ID(cur,name):
	cur.execute("SELECT cultureid FROM culture WHERE culturename=?",[name])
	cultureID = cur.fetchone()
	if cultureID!=None: cultureID=cultureID[0]
	return cultureID

def get_rel_ID(cur,name):
	cur.execute("SELECT religionid FROM religion WHERE religionname=?",[name])
	religionID = cur.fetchone()
	if religionID!=None: religionID=religionID[0]
	return religionID

def get_chars(file, cur):
	parser.jumpTo(file, "^character=")

	obj = parser.getCK2Obj(file, person_regex)
	while(not obj == None):
		religionID = None
		cultureID = None
		isMale = True
		attributes = {}
		traits = []
		
		# Integer conversions and list truncation
		try:
			id = int(obj.get("tag")) # Person id
			if("dnt" in  obj): obj["dnt"] = int(obj["dnt"])
			if("fat" in obj): obj["fat"] = int(obj["fat"])
			if("rfat" in obj): obj["rfat"] = int(obj["rfat"])
			else: obj["rfat"] = obj.get("fat")
			if("mot" in obj): obj["mot"] = int(obj["mot"]) 
			if("emp" in obj): obj["emp"] = int(obj["emp"])
			if("host" in obj): obj["host"] = int(obj["host"])
			
			if("fer" in obj): obj["fer"] = float(obj["fer"])
			if("health" in obj): obj["health"] = float(obj["health"])
			if("wealth" in obj): obj["wealth"] = float(obj["wealth"])
			if("prs" in obj): obj["prs"] = float(obj["prs"])
			if("piety" in obj): obj["piety"] = float(obj["piety"])

			if("att" in obj):
				attributes = make_person_attributes(obj["att"])

			if("tr" in obj):
				traits = make_traits(obj["tr"])
		except ValueError:
			raise Exception("ERROR: One of the person attributes is not a number!")

		if("rel" in obj): religionID = get_rel_ID(cur,obj["rel"].replace("\"", ""))
		if("cul" in obj): cultureID = get_cul_ID(cur,obj["cul"].replace("\"", ""))
		if("bn" in obj): obj["bn"] = obj["bn"].replace("\"", "")
		if("b_d" in obj): obj["b_d"] = make_date(obj["b_d"].replace("\"", ""))
		if("d_d" in obj): obj["d_d"] = make_date(obj["d_d"].replace("\"", ""))
		if("fem" in obj): isMale = False
		
		#if religion or culture is missing, default to dynasty religion and culture
		if obj.get('dnt')!=None:
			if ('rel' not in obj):
				cur.execute("SELECT religionID FROM dynasty WHERE dynastyID=?",[obj.get('dnt')])
				religionID = cur.fetchone()
				if religionID!=None: religionID=religionID[0]
			if ('cul' not in obj):
				cur.execute("SELECT cultureID FROM dynasty WHERE dynastyID=?",[obj.get('dnt')])
				cultureID = cur.fetchone()
				if cultureID!=None: cultureID=cultureID[0]
		
		cur.execute(
			'INSERT INTO Person Values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
			[id, obj.get("bn"), obj.get("dnt"), isMale, obj.get("b_d"), obj.get("d_d"), obj.get("fat"),
			 obj.get("rfat"), obj.get("mot"), religionID, cultureID, obj.get("fer"),
			 obj.get("health"), obj.get("wealth"), obj.get("prs"), obj.get("piety"),
			 obj.get("host"), obj.get("emp"), attributes.get("martial"), attributes.get("diplomacy"),
			 attributes.get("steward"), attributes.get("intrigue"), attributes.get("learning")
		])

		if(isinstance(obj.get("oh"), list)):
			for title_id in (obj["oh"]):
				if title_id[1:-1] != '---':
					cur.execute("INSERT INTO rulers VALUES(?, ?)", [id, title_id[1:-1]])
		elif obj.get("oh"):
			title_id = obj["oh"]
			cur.execute("INSERT INTO rulers VALUES(?, ?)", [id, title_id[1:-1]])

		for tr in traits:
			cur.execute("INSERT INTO trait Values(?, ?)", [id, int(tr)])

		if("spouse" in obj):
			if(isinstance(obj["spouse"], list)):
				for s in obj["spouse"]:
					cur.execute("INSERT INTO marriage Values(?, ?)",
								[id, s])
			else:
				cur.execute("INSERT INTO marriage Values(?, ?)",
							[id, obj["spouse"]])
		

		# Parse claims
		if("claim" in obj):
			if(isinstance(obj["claim"], list)):
				for claim in obj["claim"]:
					if(isinstance(claim.get("title"), dict)):
						claim["title"] = claim["title"]["title"]
					cur.execute("INSERT INTO claim Values(?, ?, ?, ?)",
								[id, claim.get("title"),
								 "pressed" in claim,
								 "weak" in claim])
			else:
				claim = obj["claim"]
				if(isinstance(claim.get("title"), dict)):
						claim["title"] = claim["title"]["title"]
				cur.execute("INSERT INTO claim Values(?, ?, ?, ?)",
							[id,
							 claim.get("title"),
							 "pressed" in claim,
							 "weak" in claim])


		obj = parser.getCK2Obj(file, person_regex);
