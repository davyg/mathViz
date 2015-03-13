import xmlrpclib
import sqlite3
import time

server = xmlrpclib.Server('http://localhost:20738/RPC2')
conn = sqlite3.connect('/home/davyg/Downloads/nasalib/Hypatheon-1.1/data/hyp-nasalib-6.0.4.sdb')

G = server.ubigraph

G.clear();

c = conn.cursor()

c.execute('''SELECT Declarations.body, Proofs.script FROM Proofs INNER JOIN Declarations ON Proofs.declaration_id=Declarations.declaration_id''')

i = 0
scripts = {}
while i > -1:
	res = c.fetchone()
	if not res:
		break
	name = res[0].partition(":")[0].strip()
	if 'TCC' in name or 'tcc' in name or name == "":
		continue
	#if name in scripts:
	#	print("BAD", res, len(scripts))
	#	break
	scripts[name] = res[1]
	i = i + 1


def findParents(name):
	res = []
	for n in scripts.keys():
		if '"' + n + '"' in scripts[name]:
			res.append(n)
	return res

def computeAncestors(name):
	x = addVertix(name)
	parents = findParents(name)
	print(name, len(parents))
	if "even" in name or "odd" in name:
		print(scripts[name])
	for n in parents:
		y = addVertix(n)
		G.new_edge(x,y)
		computeAncestors(n)


def computeChildren(name):
	res = []
	for n in scripts.keys():
		if '"' + name + '"' in scripts[n]:
			res.append(n)
	return res

def computeDescendant2(name):
	x = addVertix(name)
	children = computeChildren(name)
	for n in children:
		y = addVertix(n)
		G.new_edge(x,y)

def computeDescendant(name):
	x = addVertix(name)
	formula = '''SELECT name FROM Proofs INNER JOIN AllNames ON Proofs.name_id=AllNames.name_id WHERE (NOT (name LIKE "%tcc%")) AND script LIKE '"'''+name+'''"'; '''
	c.execute(formula)
	results = c.fetchall()
	print(name, len(results))
	for res in results:
		n = res[0].partition("-")[0]
		y = addVertix(n)
		G.new_edge(x,y)
		print("edge")
		computeChildren(n)




def computeDescendant(name):
	x = addVertix(name)
	formula = '''SELECT name FROM Proofs INNER JOIN AllNames ON Proofs.name_id=AllNames.name_id WHERE (NOT (name LIKE "%tcc%")) AND script LIKE '"'''+name+'''"'; '''


"""
proofreferences -> ref_name_id ref_theory ref_library
declarations -> decleration_id name_id theory_name library_name
"""

def test2():
	l = sorted([(x[0], len(x[1])) for x in scripts.items()], key=lambda x: x[1])
	computeAncestors(l[-1][0])

def test1():
	i = 0
	for x in scripts.keys():
		if i > 100:
			break
		computeDescendant2(x)
		i += 1

vertices = {}

def addVertix(ident, name, body):
	if not ident in vertices:
		x = G.new_vertex()
		vertices[ident] = x
		G.set_vertex_attribute(x, 'color', "#0000ff")
		if "theorem" in body.lower():
			G.set_vertex_attribute(x, 'color', "#00ff00")
			G.set_vertex_attribute(x, 'label', name)
		elif "axiom" in body.lower() or "postulate" in body.lower():
			G.set_vertex_attribute(x, 'color', "#ff0000")
			G.set_vertex_attribute(x, 'label', name)
		elif "lemma" in body.lower() or "corollary" in body.lower() or "formula" in body.lower() or "proposition" in body.lower():
			G.set_vertex_attribute(x, 'color', "##ffff0")
		else:
			print(name, body)
			raise Exception()
	return vertices[ident]

REQUEST = """
SELECT P.declaration_id, PN.name, PD.body, D.declaration_id, DN.name, D.body
FROM proofreferences AS P
INNER JOIN declarations AS PD
  ON P.declaration_id = PD.declaration_id
INNER JOIN declarations AS D
  ON D.name_id = P.ref_name_id AND P.ref_theory = D.theory AND P.ref_library = D.library
INNER JOIN allnames AS PN
  ON P.decl_name_id = PN.name_id
INNER JOIN allnames AS DN
  ON D.name_id = DN.name_id
WHERE
  P.ref_type = "formula" AND
  P.decl_type = "formula" AND
  P.library = "reals"
"""

MAX = 10000

def compute():
	c.execute(REQUEST)
	i = 0
	while i < MAX:
		res = c.fetchone()
		if not res:
			print("NO MORE")
			break
		x = addVertix(res[0], res[1], res[2])
		y = addVertix(res[3], res[4], res[5])
		G.new_edge(x,y)
		i += 1

compute()

"""
for name in names:
	x = addVertix(name)
	formula = '''SELECT name FROM Proofs INNER JOIN AllNames ON Proofs.name_id=AllNames.name_id WHERE (NOT (script LIKE "%tcc%")) AND script LIKE '"'''+name+'''"'; '''
	c.execute(formula)
	results = c.fetchall()
	print(name, len(results))
	for res in results:
		y = addVertix(res[0])
		G.new_edge(x,y)
"""

conn.close()
