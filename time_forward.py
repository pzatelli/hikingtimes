# Phyton scripts to evaluate hiking times in GRASS GIS
# Copyright (C) 2025 Gabriele Barile and Paolo Zatelli
# University of Trento
# paolo.zatelli@unitn.it

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#!/usr/bin/env python

import grass.script as gscript
import math

def main():
    gscript.run_command('g.region', flags='p')


if __name__ == '__main__':
    main()

#def mappa
for k in range(69,222):
	numero_arco=k
	arco='arco_tmp'
	mappa=arco + '_punti'

#v extract
	gscript.run_command('v.extract', overwrite=True, input='sottorete_definitiva3@sottorete', where="cat='" + str(numero_arco) + "'", output=arco)

#v to points
	gscript.run_command('v.to.points', overwrite=True, input=str(arco) + '@sottorete', output=mappa, dmax=10)

#dist e numero
	gscript.run_command('db.select', overwrite=True, flags='cv', sql="select along from " + str(mappa) +  "_2", output='along_tmp', separator='newline')
	in_file=open("along_tmp","r")
	along_tmp=in_file.read()
	in_file.close()
	along_tmp=along_tmp.split("\n")
	numero=len(along_tmp)-1
	dist=float(along_tmp[1])
#	print "numero punti=", numero
#	print "distanza punti=", dist

#colonne
	gscript.run_command('v.db.addcolumn', map=mappa, layer='2', columns='quota double')
	gscript.run_command('v.db.addcolumn', map=mappa, layer='2', columns='quota_prec double')
	gscript.run_command('v.db.addcolumn', map=mappa, layer='2', columns='delta_quota double')
	gscript.run_command('v.db.addcolumn', map=mappa, layer='2', columns='pendenza double')
	gscript.run_command('v.db.addcolumn', map=mappa, layer='2', columns='pendenza_gradi double')
	gscript.run_command('v.db.addcolumn', map=mappa, layer='2', columns='velocita double')
	gscript.run_command('v.db.addcolumn', map=mappa, layer='2', columns='tempo double')
	gscript.run_command('v.db.addcolumn', map=mappa, layer='2', columns='tempo_tot double')
	gscript.run_command('v.db.addcolumn', map=mappa, layer='2', columns='ore double')

#quota
	gscript.run_command('v.what.rast', map=mappa, layer='2', raster='dtm_sottorete', column='quota')

#quota_prec
	gscript.run_command('db.select', overwrite=True, flags='cv', sql="select quota from " + str(mappa) +  "_2 where cat<" + str(numero), output='quota_tmp', separator='newline')
	in_file=open("quota_tmp","r")
	quota_tmp=in_file.read()
	in_file.close()
	quota_tmp=quota_tmp.split("\n")
	for i in range (0,numero-1):
		gscript.run_command('db.execute', sql="UPDATE " + str(mappa) +  "_2 SET quota_prec=" + str(quota_tmp[i]) + " WHERE cat="+str(i+2))

#delta_quota
	for i in range (2,numero+1):
		gscript.run_command('db.execute', sql="UPDATE " + str(mappa) +  "_2 SET delta_quota=(quota-quota_prec) WHERE cat="+str(i))
	gscript.run_command('db.select', overwrite=True, flags='cv', sql="select delta_quota from  " + str(mappa) + "_2 where cat>1", output='delta_tmp', separator='newline')
	in_file=open("delta_tmp","r")
	delta_tmp=in_file.read()
	in_file.close()
	delta_tmp=delta_tmp.split("\n")

#pendenza e pendenza_gradi
	for i in range (0,numero-1):
		temp = float(delta_tmp[i])
		gscript.run_command('db.execute', sql="UPDATE " + str(mappa) +  "_2 SET pendenza=" + str(math.atan2(temp,dist)) + " WHERE cat="+str(i+2))
		gscript.run_command('db.execute', sql="UPDATE " + str(mappa) +  "_2 SET pendenza_gradi = pendenza*180/ " + str(math.pi) + " WHERE cat="+str(i+2))

#velocita
	a = "(0.00005*pendenza_gradi*pendenza_gradi*pendenza_gradi+0.0067*pendenza_gradi*pendenza_gradi+0.3169*pendenza_gradi+5.8524)"
	b = "(0.0012*pendenza_gradi*pendenza_gradi*pendenza_gradi-0.0194*pendenza_gradi*pendenza_gradi-0.1559*pendenza_gradi+4.2097)"
	c = "(-0.00008*pendenza_gradi*pendenza_gradi*pendenza_gradi+0.0091*pendenza_gradi*pendenza_gradi-0.3296*pendenza_gradi+4.5583)"
	d = "(0.0003*pendenza_gradi*pendenza_gradi-0.0437*pendenza_gradi+1.6718)"
	e = "(0.0002*pendenza_gradi*pendenza_gradi-0.0285*pendenza_gradi+1.162)"
	gscript.run_command('db.execute', sql="UPDATE " + str(mappa) +  "_2 SET velocita=" + str(a) + " WHERE pendenza_gradi>-45 AND pendenza_gradi<=-7")
	gscript.run_command('db.execute', sql="UPDATE " + str(mappa) +  "_2 SET velocita=" + str(b) + " WHERE pendenza_gradi>-7 AND pendenza_gradi<=4")
	gscript.run_command('db.execute', sql="UPDATE " + str(mappa) +  "_2 SET velocita=" + str(c) + " WHERE pendenza_gradi>4 AND pendenza_gradi<=25")
	gscript.run_command('db.execute', sql="UPDATE " + str(mappa) +  "_2 SET velocita=" + str(d) + " WHERE pendenza_gradi>25 AND pendenza_gradi<=80")
	gscript.run_command('db.execute', sql="UPDATE " + str(mappa) +  "_2 SET velocita=" + str(e) + " WHERE pendenza_gradi>-90 AND pendenza_gradi<=-45")

#tempo
	gscript.run_command("db.execute", sql="UPDATE "+str(mappa)+"_2 SET tempo=3.6*"+str(dist)+"/velocita")

#tempo_tot
	gscript.run_command('db.select', overwrite=True, flags='cv', sql="select tempo from " + str(mappa) + "_2 where cat>1", output='tempo_tmp', separator='newline')
	in_file=open("tempo_tmp","r")
	tempo_tmp=in_file.read()
	in_file.close()
	tempo_tmp=tempo_tmp.split("\n")
	t=0
	for i in range(0,numero-1):
	    temp=float(tempo_tmp[i])
	    t=t+temp
	    gscript.run_command('db.execute', sql="UPDATE " + str(mappa) + "_2 SET tempo_tot=" + str(t) + " WHERE cat="+str(i+2))

#ore
	gscript.run_command("db.execute", sql="UPDATE " + str(mappa) + "_2 SET ore=tempo_tot/3600")

#estrazione tempo di percorrenza
	gscript.run_command('db.select', overwrite=True, flags='cv', sql="select ore from " + str(mappa) + "_2 where cat="+str(numero), output='tempo_finale')
	in_file=open("tempo_finale","r")
	tempo_finale=in_file.read()
	in_file.close()
	tempo_finale=tempo_finale.split("\n")
	t=float(tempo_finale[0])
	gscript.run_command('db.execute', sql="UPDATE sottorete_definitiva3 SET tempo_andata="+str(t)+" WHERE cat="+str(numero_arco))

#estrazione dislivello complessivo
	gscript.run_command('db.select', overwrite=True, flags='cv', sql="select delta_quota from " + str(mappa) +  "_2 where cat>1", output='delta_quota', separator='newline')
	in_file=open("delta_quota","r")
	delta_quota=in_file.read()
	in_file.close()
	delta_quota=delta_quota.split("\n")
	dis=0
	for i in range(0,numero-1):
		temp=float(delta_quota[i])
		dis=dis+temp
	gscript.run_command('db.execute', sql="UPDATE sottorete_definitiva3 SET dislivello_effettivo_andata="+str(dis)+" WHERE cat="+str(numero_arco))
