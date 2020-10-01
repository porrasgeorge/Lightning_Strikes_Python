import simplekml
kml = simplekml.Kml()
pnt = kml.newpoint(name="BallonStyle", coords=[(18.429191, -33.987286)])
pnt.style.balloonstyle.text = '''<b><font color="#CC0000" size="+3">$[name]</font></b>
<br/>
<br/>
<font face="Courier">aaa</font>
<br/>
<br/>
Extra text that will appear in the description balloon
<br/>
<br/>
<TABLE BORDER="1">
<TR>
<TH>&nbsp;</TH>
<TH>Config 1</TH>
</TR>
<TR>
<TH>Cost A</TH>
<TD>1</TD>
</TR>
<TR>
<TH>Cost B</TH>
<TD>10</TD>
</TR>
</TABLE>'''
# pnt.style.balloonstyle.bgcolor = simplekml.Color.lightgreen
# pnt.style.balloonstyle.textcolor = simplekml.Color.rgb(0, 0, 255)
kml.save("BalloomStyle.kml")