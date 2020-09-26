import simplekml
kml = simplekml.Kml()
pol = kml.newpolygon(name='A Polygon')
pol.outerboundaryis = [(18.333868,-34.038274), (18.370618,-34.034421),
                       (18.350616,-34.051677),(18.333868,-34.038274)]
pol.innerboundaryis = [(18.347171,-34.040177), (18.355741,-34.039730),
                       (18.350467,-34.048388),(18.347171,-34.040177)]
kml.save("Polygon.kml")