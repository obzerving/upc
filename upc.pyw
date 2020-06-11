##################################################################################################################
#                                                                                                                #
# Universal Polygon Calculator                                                                                   #
# Version 1.0                                                                                                    #
#                                                                                                                #
# This program generates an SVG file                                                                             #
#   - Given an SVG file containing two paths representing the left and right profile of stacked n-sided polygons #
#   - Generate a paper model of one of the n sides with tabs to assemble into a full 3D model                    #
#   - Generate top and bottom lids for the generated model                                                       #
#   - A wrapper to cover the generated model                                                                     #
#                                                                                                                #
# Copyright: (c) 2020, Joseph Zakar <observing@gmail.com>                                                        #
# GNU General Public License v3.0+ (see LICENSE or                                                               #
# https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)#fulltext)                                  #
#                                                                                                                #
##################################################################################################################

# Init variables
import sys
import os
import uuid
from xml.dom.minidom import parse
import xml.dom.minidom
from svgpathtools import *
import math
import tkinter
from tkinter import *
import tkinter.filedialog
import tkinter.font as font
from tkinter import messagebox

# user defaults
inputfile = ''
outputfile = ''
numpoly = 6
tab_height = 0.4
dashlength = 0.25
nohscores = 0

# non-user defaults
orientTop = 0
orientBottom = 1
orientRight = 2
orientLeft = 3
tab_angle = 25.0

def main(argv):
   global inputfile
   global outputfile
   global numpoly
   global dashlength
   global nohscores
   global tab_height
   global orientTop
   global orientBottom
   global orientRight
   global orientLeft
   global tab_angle
   
   top = tkinter.Tk()
   top.title("Universal Polygon Calculator")
   pane = PanedWindow(top, orient=VERTICAL)
   pane.pack(fill=BOTH, expand=1)
   F1 = Frame(pane)
   L1 = tkinter.Label(F1, text="Input File Name   ")
   L1.pack( side = tkinter.LEFT)
   E1 = tkinter.Entry(F1, bd =5, width=30)
   E1.pack(side = tkinter.LEFT)
   F2 = Frame(pane)
   L2 = tkinter.Label(F2, text="Output File Name")
   L2.pack( side = tkinter.LEFT)
   E2 = tkinter.Entry(F2, bd =5, width=30)
   E2.pack(side = tkinter.LEFT)
   F3 = Frame(pane)
   L3 = tkinter.Label(F3, text="Number of Polygon Sides")
   L3.pack( side = tkinter.LEFT)
   E3 = tkinter.Entry(F3, bd =5, width=5)
   E3.insert(0,str(numpoly))
   E3.pack(side = tkinter.LEFT)
   F4 = Frame(pane)
   L4 = tkinter.Label(F4, text="Length of Dashline in inches (zero for solid line)")
   L4.pack( side = tkinter.LEFT)
   E4 = tkinter.Entry(F4, bd =5, width=6)
   E4.insert(0,str(dashlength))
   E4.pack(side = tkinter.LEFT)
   F4a = Frame(pane)
   L4a = tkinter.Label(F4a, text="Height of Tab in inches")
   L4a.pack( side = tkinter.LEFT)
   E4a = tkinter.Entry(F4a, bd =5, width=6)
   E4a.insert(0,str(tab_height))
   E4a.pack(side = tkinter.LEFT)
   F5 = Frame(pane)
   toggleState = IntVar()
   C1 = Checkbutton(F5, text="Only place scorelines where there are Tabs", variable=toggleState)
   C1.pack(side = tkinter.LEFT)

   # This is the handler for the input file browse button
   def InfileCallBack():
      ftypes = [('svg files','.svg'), ('All files','*')]
      inputfile = tkinter.filedialog.askopenfilename(title = "Select File", filetypes = ftypes, defaultextension='.svg')
      E1.delete(0,tkinter.END)
      E1.insert(0, inputfile)

   # This is the handler for the output file browse button
   def OutfileCallBack():
      ftypes = [('svg files','.svg'), ('All files','*')]
      outputfile = tkinter.filedialog.asksaveasfilename(title = "Save File As", filetypes = ftypes, defaultextension='.svg')
      E2.delete(0,tkinter.END)
      E2.insert(0,outputfile)

   # This is the handler for the cancel button
   def CancelCallBack():
      top.destroy()

   # This is the handler for the OK button
   def OKCallBack():
      global inputfile
      global outputfile
      global numpoly
      global dashlength
      global nohscores
      global tab_height
      inputfile = E1.get()
      outputfile = E2.get()
      numpoly = int(E3.get())
      dashlength = float(E4.get())
      tab_height = float(E4a.get())
      nohscores = toggleState.get()
      top.destroy()

   axis = 1 # We are not implementing the 'reverse Y axis' option at this time
   lhs = 0
   rhs = 1
   lasty1 = 0.0
   lastw1 = 0.0
   lasty2 = 0.0
   lastw2 = 0.0
   dscores = [] # temporary list of all score lines
   opaths = []  # all the generated paths will be stored in this list to write an SVG file
   oattributes = [] # each path in opaths has a corresponding set of attributes in this list
   # attributes for body, top, and bottom
   battributes = {'style' : 'fill:#32c864;stroke:#000000;stroke-width:0.96;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dashoffset:0;stroke-opacity:1'}
   # attributes for wrapper
   wattributes = {'style' : 'fill:#6432c8;stroke:#000000;stroke-width:0.96;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dashoffset:0;stroke-opacity:1'}
   # attributes for scorelines
   sattributes = {'style' : 'fill:none;stroke:#000000;stroke-width:0.96;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dashoffset:0;stroke-opacity:1'}
   B1 = tkinter.Button(F1, text="Browse", command=InfileCallBack)
   B1.pack(side = tkinter.LEFT)
   B2 = tkinter.Button(F2, text="Browse", command=OutfileCallBack)
   B2.pack(side = tkinter.LEFT)
   F6 = Frame(pane)
   bfont = font.Font(size=12)
   B3 = tkinter.Button(F6, text="Cancel", command=CancelCallBack)
   B3['font'] = bfont
   B3.pack(side = tkinter.LEFT, ipadx=30)
   B4 = tkinter.Button(F6, text="OK", command=OKCallBack)
   B4['font'] = bfont
   B4.pack(side = tkinter.RIGHT,ipadx=40)
   pane.add(F1)
   pane.add(F2)
   pane.add(F3)
   pane.add(F4)
   pane.add(F4a)
   pane.add(F5)
   pane.add(F6)
   top.mainloop()
   if axis == -1:
      root = tkinter.Tk()
      root.withdraw()
      messagebox.showinfo('UPC Program Info', 'Orientation of Y Axis will be Reversed', parent=root)
   if inputfile == '':
      root = tkinter.Tk()
      root.withdraw()
      messagebox.showerror('UPC Input Error', 'Input File is Required', parent=root)
      sys.exit(5)
   if outputfile == '':
      root = tkinter.Tk()
      root.withdraw()
      messagebox.showerror('UPC Input Error', 'Output File is Required', parent=root)
      sys.exit(5)
   # Parse input file into paths, attributes, and svg_attributes
   ipaths, iattributes, isvg_attributes = svg2paths2(inputfile)
   # determine the units and the scale of the input file
   # Check the units to see if we support them
   hwunits = isvg_attributes['height'][-2:]
   if(hwunits != 'in'):
      root = tkinter.Tk()
      root.withdraw()
      messagebox.showerror('UPC Input Error', 'Document Units Must be in Inches', parent=root)
      sys.exit(6)
   inheight = float(isvg_attributes['height'][:-2])
   inwidth = float(isvg_attributes['width'][:-2])
   invb = isvg_attributes['viewBox'].split()
   # Assumes X and Y scales are equal
   inscale = inwidth/float(invb[2])
   ## Ensure there is only one pair of paths
   if len(ipaths) != 2:
      root = tkinter.Tk()
      root.withdraw()
      messagebox.showerror('UPC Input Error', 'The input file should contain only two paths representing the left and right sides of the profile.', parent=root)
      sys.exit(3)
   ## NOTE: We are assuming that the order of nodes in one path corresponds to the same order of nodes in the other path (i.e same Y values)
   # Calculate center axis
   if round(ipaths[0][0][0].imag,5) != round(ipaths[1][0][0].imag,5):
      # Y values are not the same (to fifth decimal place). So much for our assumption
      root = tkinter.Tk()
      root.withdraw()
      messagebox.showerror('UPC Input Error', 'The order of nodes in the left hand path needs to correspond to the same order in the right hand path.', parent=root)
      sys.exit(4)
   if ipaths[0][0][0].real > ipaths[1][0][0].real:
      # The second path is the left hand side
      lhs = 1
      rhs = 0
   xcenter = (ipaths[lhs][0][0].real + (ipaths[rhs][0][0].real - ipaths[lhs][0][0].real)/2.0)*inscale
   # Calculate points / line segments
   nlhs = []
   nrhs =[]
   dstr = ipaths[lhs].d()
   inodes = dstr.split()
   pointype = "XX"
   for coord in range(len(inodes)):
      if inodes[coord] == 'M': # Next two comma separted numbers are first XY point
         pointype = 'M'
      elif inodes[coord] == 'L': # Next two comma separted numbers are XY point to line from last point
         pointype = 'L'
      elif inodes[coord] == 'H': # Next number is X value of a line to last point
         pointype = 'H'
      elif inodes[coord] == 'V': # Next number is Y value of a line to last point
         pointype = 'V'
      elif inodes[coord] == 'Z': # End of path. Nothing after Z
         pointype = 'Z'
      else:
         if (pointype == 'M') or (pointype == 'L'):
            ipoint = inodes[coord].split(',')
         elif pointype == 'H':
            ipoint = inodes[coord]+','+inodes[coord-1].split()[1]
         elif pointype == 'V':
            ipoint = inodes[coord-1].split()[0]+','+inodes[coord]
         ## Find the distance between corresponding nodes and their Y position
         w1 = (xcenter - float(ipoint[0])*inscale)*2.0
         y1 = float(ipoint[1])*inscale
         ## Recalculate new distance (width of one polygon side) and new Y position
         w2 = w1*math.sin(math.pi/numpoly) * (1-(numpoly%2)) + ((0.5*w1)/math.cos(math.radians((360/numpoly)/2))) * (numpoly%2)
         if (pointype == 'M'):
            y2 = y1
         else:
            y2 = math.sqrt((abs(w2/(2*math.tan(math.radians(180/numpoly)))-lastw2/(2*math.tan(math.radians(180/numpoly))))**2)+(abs(y1-lasty1)**2)) + (lasty2*axis)
         ## Calculate new X position based on center axis
         x2lhs = xcenter - w2/2
         x2rhs = xcenter + w2/2
         ## Build a lhs and rhs list of points
         nlhs.append(complex(x2lhs, y2))
         nrhs.append(complex(x2rhs, y2))
         if nohscores == 0:
            # As long as we are here, put a score mark between the corresponding left and right points (except top and bottom)
            if (pointype != "XX") and (coord != (len(inodes) -1)):
               spaths = makescore(complex(x2lhs, y2), complex(x2rhs, y2), dashlength)
               dscores.append(spaths)
         # lastly, update our state variables
         lasty1 = y1
         lasty2 = y2
         lastw1 = w1
         lastw2 = w2
   ## At this point, we can generate the top and bottom polygons
   ## r = sidelength/(2*sin(PI/numpoly))
   opaths.append(makepoly(nrhs[-1].real - nlhs[-1].real, numpoly))
   oattributes.append(battributes)
   opaths.append(makepoly(nrhs[0].real - nlhs[0].real, numpoly))
   oattributes.append(battributes)
   ## Reverse the order of rhs points so we can concatenate them with lhs
   nrhs.reverse()
   mpaths = makepath(nlhs, nrhs)
   opaths.append(mpaths)
   oattributes.append(wattributes)
   # Create tabs for each line segment of right hand path
   trhs = [nrhs[0]]
   for nodes in range(len(nrhs)-1):
      # Assuming that nodes are ordered in descending Y
      tabpt1, tabpt2 = makeTab(nrhs[nodes], nrhs[nodes+1], orientRight)
      trhs.append(tabpt1)
      trhs.append(tabpt2)
      trhs.append(nrhs[nodes+1])
      ## Create score line where line segment was
      spaths = makescore(nrhs[nodes], nrhs[nodes+1],dashlength)
      dscores.append(spaths)
   nrhs.clear()
   nrhs = trhs.copy()
   trhs.clear()
   ## put a tab and scoreline on the top
   spaths = makescore(nlhs[0], nrhs[-1],dashlength)
   dscores.append(spaths)
   tabpt1, tabpt2 = makeTab(nlhs[0], nrhs[-1], orientTop)
   nrhs.append(tabpt2)
   nrhs.append(tabpt1)
   ## put a tab and scoreline on the bottom
   spaths = makescore(nlhs[-1], nrhs[0],dashlength)
   dscores.append(spaths)
   tabpt1, tabpt2 = makeTab(nlhs[-1], nrhs[0], orientBottom)
   nlhs.append(tabpt1)
   nlhs.append(tabpt2)
   # Create the path for the shape
   outpath = makepath(nlhs, nrhs)
   opaths.append(outpath)
   oattributes.append(battributes)
   # lump together all the score lines into one path
   slist = ''
   for dndx in dscores:
      slist = slist + dndx
   opaths.append(parse_path(slist))
   oattributes.append(sattributes)
   osvg_attributes = {}
   for ia in isvg_attributes:
      if ((((ia != 'xmlns:dc') and  (ia != 'xmlns:cc')) and (ia != 'xmlns:rdf')) and (ia != 'xmlns:svg')):
         osvg_attributes[ia] = isvg_attributes[ia]
   totalpaths = Path()
   for tps in opaths:
      totalpaths.append(tps)
   xmin,xmax,ymin,ymax=totalpaths.bbox()
   # Write new paths, attributes, and svg_attributes to output file
   #oattributes.append(iattributes[0])
   tmpfile = str(uuid.uuid4())
   #wsvg(opaths, attributes=oattributes, svg_attributes=osvg_attributes, filename=tmpfile)
   wsvg(opaths, filename=tmpfile, attributes=oattributes)
   # Post processing stage
   # Due to issues with svgpathtools, some post processing of the file output from the library is necessary until issues have been resolved
   # The following attributes are suitable for input to inkscape and/or the Cricut Design Space
   # Document properties are 11.5 x 11.5 inches. The viewBox sets the scale at 72 dpi. Change the display units in Inkscape to inches.
   docscale = 72
   isvg_attributes = {'xmlns:dc': 'http://purl.org/dc/elements/1.1/', 'xmlns:cc': 'http://creativecommons.org/ns#', 'xmlns:rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'xmlns:svg': 'http://www.w3.org/2000/svg', 'xmlns': 'http://www.w3.org/2000/svg', 'id': 'svg8', 'version': '1.1', 'viewBox': '0 0 828.0 828.0', 'height': '11.5in', 'width': '11.5in'}
   # Assumes order of paths is top, bottom, wrapper, body, scorelines
   ids = ['top','bottom','wrapper','body','scorelines']
   # Read the xml tree from the file
   DOMTree = xml.dom.minidom.parse(tmpfile)
   # Accessing the svg node (which must be the root element)
   svg =DOMTree.documentElement
   # correct the height, width, and viewBox attributes
   svg.setAttribute('height', isvg_attributes['height'])
   svg.setAttribute('width', isvg_attributes['width'])
   svg.setAttribute('viewBox', isvg_attributes['viewBox'])
   # All path nodes under svg
   paths = svg.getElementsByTagName("path")
   wbbox = xmax-xmin
   hbbox = ymax-ymin
   strwidth = isvg_attributes['width']
   if not(strwidth.isdigit()):
      # For now, assume it is a two character unit at the end of the string
      # TODO: Process the units field and modify paths accordingly
      midbbox = (float(strwidth[:-2])-wbbox)/2 -xmin
   else:
      midbbox = (float(strwidth)-wbbox)/2 -xmin
   strheight = isvg_attributes['height']
   if not(strwidth.isdigit()):
      # For now, assume it is a two character unit at the end of the string
      # TODO: Process the units field and modify paths accordingly
      centerbbox = (float(strheight[:-2])-hbbox)/2 -ymin
   else:
      centerbbox = (float(strheight)-hbbox)/2 -ymin
   for p in range(len(paths)):
      # Change paths to close with z rather than repeating first point
      inodes = paths[p].getAttribute('d').split()
      dstr = ''
      firstpoint = ''
      lastpoint = ''
      rplcoord = 0
      process = 1
      for coord in range(len(inodes)):
         if not((inodes[coord] == 'M') or (inodes[coord] == 'L')):
            if firstpoint == '':
               firstpoint = inodes[coord]
            elif coord == len(inodes)-1: # check last point
               if inodes[coord] == firstpoint: # does it repeat first point
                  dstr = dstr + 'z' # yes. replace it with a z
                  process = 0 # and stop processing
               else:
                  ipoint = inodes[coord].split(',')
                  dstr = dstr + cstr + str((float(ipoint[0])+midbbox)*docscale) + ',' + str((float(ipoint[1])+centerbbox)*docscale) + ' '
                  process = 0
            if(process == 1):
               ipoint = inodes[coord].split(',')
               dstr = dstr + cstr + str((float(ipoint[0])+midbbox)*docscale) + ',' + str((float(ipoint[1])+centerbbox)*docscale) + ' '
            else:
               paths[p].setAttribute('d', dstr) # and replace the path
         else:
            cstr = inodes[coord] + ' '
      # Update the path ids to something more meaningful
      paths[p].setAttribute('id',ids[p])
   with open(outputfile,'w') as xml_file:
      DOMTree.writexml(xml_file, indent="\t", newl="\n")
   try:
      os.remove(tmpfile)
   except OSError:
      pass   
   root = tkinter.Tk()
   root.withdraw()
   messagebox.showinfo("UPC", "width = "+str(round(xmax-xmin,3))+", height = "+str(round(ymax-ymin,3)), parent=root)

def makepoly(sidelength, numpoly):
   # Returns a numpoly-sided polygon whose side length is sidelength as a closed path
   r = sidelength/(2*math.sin(math.pi/numpoly))
   pstr = 'M'
   for ppoint in range(0,numpoly):
      xn = r*math.cos(2*math.pi*ppoint/numpoly)
      yn = r*math.sin(2*math.pi*ppoint/numpoly)
      pstr = pstr + ' ' + str(xn) + ',' + str(yn)
   pstr = pstr + ' z' # Close the path
   ppaths = parse_path(pstr)
   return ppaths

def makescore(pt1, pt2, dashlength):
   # Draws a dashed line of dashlength between complex points
   # Assuming pt1y > pt2y
   # Dash = dashlength (in inches) space followed by dashlength mark
   # if dashlength is zero, we want a solid line
   if dashlength == 0:
      ddash = 'M '+str(pt1.real)+','+str(pt1.imag)+' L '+str(pt2.real)+','+str(pt2.imag)
   else:
      if pt1.imag == pt2.imag:
         # We are drawing horizontal dash lines. Assume pt1x < pt2x
         xcushion = pt2.real - dashlength
         ddash = ''
         xpt = pt1.real
         ypt = pt1.imag
         done = False
         while not(done):
            if (xpt + dashlength*2) <= xcushion:
               xpt = xpt + dashlength
               ddash = ddash + 'M ' + str(xpt) + ',' + str(ypt) + ' '
               xpt = xpt + dashlength
               ddash = ddash + 'L ' + str(xpt) + ',' + str(ypt) + ' '
            else:
               done = True
      elif pt1.real == pt2.real:
         # We are drawing vertical dash lines.
         ycushion = pt2.imag + dashlength
         ddash = ''
         xpt = pt1.real
         ypt = pt1.imag
         done = False
         while not(done):
            if(ypt - dashlength*2) >= ycushion:
               ypt = ypt - dashlength         
               ddash = ddash + 'M ' + str(xpt) + ',' + str(ypt) + ' '
               ypt = ypt - dashlength
               ddash = ddash + 'L ' + str(xpt) + ',' + str(ypt) + ' '
            else:
               done = True
      else:
         # We are drawing an arbitrary dash line
         m = (pt1.imag-pt2.imag)/(pt1.real-pt2.real)
         theta = math.atan(m)
         msign = (m>0) - (m<0)
         ycushion = pt2.imag + dashlength*math.sin(theta)
         xcushion = pt2.real + msign*dashlength*math.cos(theta)
         ddash = ''
         xpt = pt1.real
         ypt = pt1.imag
         done = False
         while not(done):
            nypt = ypt - dashlength*2*math.sin(theta)
            nxpt = xpt - msign*dashlength*2*math.cos(theta)
            if (nypt >= ycushion) and (((m<0) and (nxpt <= xcushion)) or ((m>0) and (nxpt >= xcushion))):
               # move to end of space / beginning of mark
               xpt = xpt - msign*dashlength*math.cos(theta)
               ypt = ypt - msign*dashlength*math.sin(theta)
               ddash = ddash + 'M ' + str(xpt) + ',' + str(ypt) + ' '
               # draw the mark
               xpt = xpt - msign*dashlength*math.cos(theta)
               ypt = ypt - msign*dashlength*math.sin(theta)
               ddash = ddash + 'L' + str(xpt) + ',' + str(ypt) + ' '
            else:
               done = True
   return ddash

def makepath(lhs,rhs):
   ## Concatenate the lhs with the rhs and turn it into a closed path
   ishape = lhs + rhs
   ## Build d property from points
   dprop = 'M'
   for nodes in range(len(ishape)):
      dprop = dprop + ' ' + str(ishape[nodes].real) + ',' + str(ishape[nodes].imag)
   ## and close the path
   dprop = dprop + ' z'
   dpaths = parse_path(dprop)
   return dpaths

def makeTab(pt1, pt2, orient):
   global orientTop
   global orientBottom
   global orientRight
   global orientLeft
   global tab_height
   global tab_angle
   switched = 0
   rpt1x = rpt1y = rpt2x = rpt2y = 0.0
   tabDone = False
   currTabHt = tab_height
   currTabAngle = tab_angle
   while not tabDone:
      if (orient == orientTop) or (orient == orientBottom):
         if pt1.real > pt2.real:
            ppt1 = pt2
            ppt2 = pt1
            switched = 1
         else:
            ppt1 = pt1
            ppt2 = pt2
         if orient == orientTop:
            TBset = -1
         elif orient == orientBottom:
            TBset = 1
         tp1 = complex(0, TBset*currTabHt) 
         tp2 = complex(0, TBset*currTabHt)
         rtp1x = tp1.real*math.cos(math.radians(-TBset*currTabAngle)) - tp1.imag*math.sin(math.radians(-TBset*currTabAngle)) + ppt1.real
         rtp1y = tp1.imag*math.cos(math.radians(-TBset*currTabAngle)) + tp1.real*math.sin(math.radians(-TBset*currTabAngle)) + ppt1.imag
         rtp2x = tp2.real*math.cos(math.radians(TBset*currTabAngle)) - tp2.imag*math.sin(math.radians(TBset*currTabAngle)) + ppt2.real
         rtp2y = tp2.imag*math.cos(math.radians(TBset*currTabAngle)) + tp2.real*math.sin(math.radians(TBset*currTabAngle)) + ppt2.imag
      elif (orient == orientRight) or (orient == orientLeft):
         if pt1.imag < pt2.imag:
            ppt1 = pt2
            ppt2 = pt1
            switched = 1
         else:
            ppt1 = pt1
            ppt2 = pt2
         if orient == orientRight:
            TBset = -1
         else: # orient == orientLeft
            TBset = 1
         tp1 = complex(-TBset*currTabHt, 0)
         tp2 = complex(-TBset*currTabHt, 0)
         rtp1x = tp1.real*math.cos(math.radians(TBset*currTabAngle)) - tp1.imag*math.sin(math.radians(TBset*currTabAngle)) + ppt1.real
         rtp1y = tp1.imag*math.cos(math.radians(TBset*currTabAngle)) + tp1.real*math.sin(math.radians(TBset*currTabAngle)) + ppt1.imag
         rtp2x = tp2.real*math.cos(math.radians(-TBset*currTabAngle)) - tp2.imag*math.sin(math.radians(-TBset*currTabAngle)) + ppt2.real
         rtp2y = tp2.imag*math.cos(math.radians(-TBset*currTabAngle)) + tp2.real*math.sin(math.radians(-TBset*currTabAngle)) + ppt2.imag
         # Check for vertical line. If so, we are already done
         if (ppt1.real != ppt2.real):
            slope = (ppt1.imag - ppt2.imag)/(ppt1.real - ppt2.real)
            theta = math.degrees(math.atan(slope))
            # create a line segment from ppt1 to rtp1
            td1 = 'M '+str(ppt1.real)+' '+str(ppt1.imag)+' '+str(rtp1x)+' '+str(rtp1y)
            rrtp1 = parse_path(td1)
            # create a line segment from ppt2 to rtp2
            td2 = 'M '+str(ppt2.real)+' '+str(ppt2.imag)+' '+str(rtp2x)+' '+str(rtp2y)
            rrtp2 = parse_path(td2)
            if orient == orientRight:
               # rotate the points theta degrees
               if slope < 0:
                  rtp1 = rrtp1.rotated(90+theta, ppt1)
                  rtp2 = rrtp2.rotated(90+theta, ppt2)
               else:
                  rtp1 = rrtp1.rotated(-90+theta, ppt1)
                  rtp2 = rrtp2.rotated(-90+theta, ppt2)
            if orient == orientLeft:
               # rotate the points theta degrees
               if slope < 0:
                  rtp1 = rrtp1.rotated(90+theta, ppt1)
                  rtp2 = rrtp2.rotated(90+theta, ppt2)
               else:
                  rtp1 = rrtp1.rotated(-90+theta, ppt1)
                  rtp2 = rrtp2.rotated(-90+theta, ppt2)
            rtp1x = rtp1[0][1].real
            rtp1y = rtp1[0][1].imag
            rtp2x = rtp2[0][1].real
            rtp2y = rtp2[0][1].imag
      if detectIntersect(ppt1.real, ppt1.imag, rtp1x, rtp1y, ppt2.real, ppt2.imag, rtp2x, rtp2y):
         currTabAngle = currTabAngle - 1.0
         if currTabAngle < 2.0:
            currTabHt = currTabHt - 0.1
            currTabAngle = tab_angle
      else:
         tabDone = True
   p1 = complex(rtp1x,rtp1y)
   p2 = complex(rtp2x,rtp2y)
   if switched == 0:
      return p1, p2
   else:
      return p2, p1

def detectIntersect(x1, y1, x2, y2, x3, y3, x4, y4):
   td = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
   if td == 0:
      # These line segments are parallel
      return false
   t = ((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4))/td
   if (0.0 <= t) and (t <= 1.0):
      return True
   else:
      return False
      
# Clean up
if __name__ == "__main__":
   main(sys.argv[1:])# Ensure that arguments are valid
