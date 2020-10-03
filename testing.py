import simplekml
kml = simplekml.Kml()
pnt = kml.newpoint(name='A Point')
pnt.timestamp.when = 2011
kml.save("TimeStamp.kml")