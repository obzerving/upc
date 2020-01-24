################################
#                              #
# Universal Polygon Calculator #
# Version 1.0                  #
#                              #
################################
# Copyright: (c) 2020, Joseph Zakar <observing@gmail.com>
# GNU General Public License v3.0+ (see LICENSE or https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)#fulltext)

# Init variables
import sys
from svgpathtools import *
import math
import tkinter
from tkinter import *
import tkinter.filedialog
import tkinter.font as font
from tkinter import messagebox

inputfile = ''
outputfile = ''
numpoly = 0
dashlength = 0.25
nohscores = 0

def main(argv):
   global inputfile
   global outputfile
   global numpoly
   global dashlength
   global nohscores
   
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
   E3.insert(0,'6')
   E3.pack(side = tkinter.LEFT)
   F4 = Frame(pane)
   L4 = tkinter.Label(F4, text="Length of Dashline in inches (zero for solid line)")
   L4.pack( side = tkinter.LEFT)
   E4 = tkinter.Entry(F4, bd =5, width=5)
   E4.insert(0,'.175')
   E4.pack(side = tkinter.LEFT)
   F5 = Frame(pane)
   toggleState = IntVar()
   C1 = Checkbutton(F5, text="Only place scorelines where there are Tabs", variable=toggleState)
   C1.pack(side = tkinter.LEFT)

   def InfileCallBack():
      ftypes = [('svg files','.svg'), ('All files','*')]
      inputfile = tkinter.filedialog.askopenfilename(title = "Select File", filetypes = ftypes, defaultextension='.svg')
      E1.insert(0, inputfile)
   def OutfileCallBack():
      ftypes = [('svg files','.svg'), ('All files','*')]
      outputfile = tkinter.filedialog.asksaveasfilename(title = "Save File As", filetypes = ftypes, defaultextension='.svg')
      E2.insert(0,outputfile)
   def CancelCallBack():
      top.destroy()
   def OKCallBack():
      global inputfile
      global outputfile
      global numpoly
      global dashlength
      global nohscores
      inputfile = E1.get()
      outputfile = E2.get()
      numpoly = int(E3.get())
      dashlength = float(E4.get())
      nohscores = toggleState.get()
      top.destroy()
   
   axis = 1
   lhs = 0
   rhs = 1
   lasty1 = 0.0
   lastw1 = 0.0
   lasty2 = 0.0
   lastw2 = 0.0
   dscores = [] # temporary list of all score lines
   opaths = []
   oattributes = []
   sattributes = {'style' : 'fill:none;stroke:#000000;stroke-width:0.01;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dashoffset:0;stroke-opacity:1'}
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
   pane.add(F5)
   pane.add(F6)
   top.mainloop()
   if axis == -1:
      print('INFO: Orientation of Y axis is reversed')
   if inputfile == '':
      print('ERROR: Input file is required')
      sys.exit(5)
   if outputfile == '':
      print('ERROR: Output file is required')
      sys.exit(5)
   # Parse input file into paths, attributes, and svg_attributes
   ipaths, iattributes, isvg_attributes = svg2paths2(inputfile)
   ## Ensure there is only one pair of paths
   if len(ipaths) != 2:
      print("The input file should contain only two paths representing the left and right sides of the model's profile.")
      sys.exit(3)
   ## NOTE: We are assuming that the order of nodes in one path corresponds to the same order of nodes in the other path (i.e same Y values)
   # Calculate center axis
   if ipaths[0][0][0].imag != ipaths[1][0][0].imag:
      # Y values are not the same. So much for our assumption
      print("It doesn't look like the order of nodes in the left hand path corresponds to the same order in the right hand path.")
      sys.exit(4)
   if ipaths[0][0][0].real > ipaths[1][0][0].real:
      # The second path is the left hand side
      lhs = 1
      rhs = 0
   xcenter = ipaths[lhs][0][0].real + (ipaths[rhs][0][0].real - ipaths[lhs][0][0].real)/2.0
   # Calculate points / line segments
   nlhs = []
   nrhs =[]
   dstr = ipaths[lhs].d()
   inodes = dstr.split()
   firstpoint = 0
   for coord in range(len(inodes)):
      if not((inodes[coord] == 'M') or (inodes[coord] == 'L')): ## Skip over M and L
         ## Find the distance between corresponding nodes and their Y position
         ipoint = inodes[coord].split(',')
         w1 = (xcenter - float(ipoint[0]))*2.0
         y1 = float(ipoint[1])
         ## Recalculate new distance (width of one polygon side) and new Y position
         w2 = w1*math.sin(math.pi/numpoly) * (1-(numpoly%2)) + ((0.5*w1)/math.cos(math.radians((360/numpoly)/2))) * (numpoly%2)
         if firstpoint == 0:
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
            if (firstpoint != 0) and (coord != (len(inodes) -1)):
               spaths = makescore(complex(x2lhs, y2), complex(x2rhs, y2), dashlength)
               dscores.append(spaths)
         # lastly, update our state variables
         firstpoint = 1
         lasty1 = y1
         lasty2 = y2
         lastw1 = w1
         lastw2 = w2
   ## At this point, we can generate the top and bottom polygons
   ## r = sidelength/(2*sin(PI/numpoly))
   opaths.append(makepoly(nrhs[0].real, nlhs[0].real, numpoly))
   oattributes.append(iattributes[0])
   opaths.append(makepoly(nrhs[-1].real, nlhs[-1].real, numpoly))
   oattributes.append(iattributes[0])
   ## Reverse the order of rhs points so we can concatenate them with lhs
   nrhs.reverse()
   mpaths = makepath(nlhs, nrhs)
   opaths.append(mpaths)
   oattributes.append(iattributes[0])
   # Create tabs for each line segment of right hand path if line segment > 1/4 inch
   trhs = [nrhs[0]]
   for nodes in range(len(nrhs)-1):
      # Assuming that nodes are ordered in descending Y
      tabpt1, tabpt2 = maketab(nrhs[nodes], nrhs[nodes+1], 0)
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
   tabpt1, tabpt2 = maketab(nlhs[0], nrhs[-1], 1)
   nrhs.append(tabpt2)
   nrhs.append(tabpt1)
   ## put a tab and scoreline on the bottom
   spaths = makescore(nlhs[-1], nrhs[0],dashlength)
   dscores.append(spaths)
   tabpt1, tabpt2 = maketab(nlhs[-1], nrhs[0], -1)
   nlhs.append(tabpt1)
   nlhs.append(tabpt2)
   # Create the path for the shape
   outpath = makepath(nlhs, nrhs)
   opaths.append(outpath)
   oattributes.append(iattributes[0])
   # lump together all the score lines into one path
   slist = ''
   for dndx in dscores:
      slist = slist + dndx
   opaths.append(parse_path(slist))
   oattributes.append(iattributes[0])
   osvg_attributes = {}
   for ia in isvg_attributes:
      if ((((ia != 'xmlns:dc') and  (ia != 'xmlns:cc')) and (ia != 'xmlns:rdf')) and (ia != 'xmlns:svg')):
         osvg_attributes[ia] = isvg_attributes[ia]
   totalpaths = Path()
   for tps in opaths:
      totalpaths.append(tps)
   xmin,xmax,ymin,ymax=totalpaths.bbox()
   # Write new paths, attributes, and svg_attributes to output file
   oattributes.append(iattributes[0])
   wsvg(opaths, attributes=oattributes, svg_attributes=osvg_attributes, filename=outputfile)
   root = tkinter.Tk()
   root.withdraw()
   messagebox.showinfo("UPC", "width = "+str(xmax-xmin)+", height = "+str(ymax-ymin), parent=root)

def makepoly(pt1, pt2, numpoly):
   # Assuming pt1 > pt2
   toplength = pt1 - pt2
   r = toplength/(2*math.sin(math.pi/numpoly))
   pstr = 'M'
   for ppoint in range(0,numpoly):
      xn = r*math.cos(2*math.pi*ppoint/numpoly)
      yn = r*math.sin(2*math.pi*ppoint/numpoly)
      pstr = pstr + ' ' + str(xn) + ',' + str(yn)
      if ppoint == 0:
         x0 = xn
         y0 = yn
   pstr = pstr + ' ' + str(x0) + ',' + str(y0)
   ppaths = parse_path(pstr)
   return ppaths

def makescore(pt1, pt2, dashlength):
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
               ddash = ddash + 'M ' + str(xpt) + ' ' + str(ypt) + ' '
               ypt = ypt - dashlength
               ddash = ddash + 'L ' + str(xpt) + ' ' + str(ypt) + ' '
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
               ddash = ddash + 'M ' + str(xpt) + ' ' + str(ypt) + ' '
               # draw the mark
               xpt = xpt - msign*dashlength*math.cos(theta)
               ypt = ypt - msign*dashlength*math.sin(theta)
               ddash = ddash + 'L' + str(xpt) + ' ' + str(ypt) + ' '
            else:
               done = True
   return ddash

def makepath(lhs,rhs):
   ## Now we can concatenate the lhs with the rhs
   ishape = lhs + rhs
   ## Build d property from points
   dprop = 'M'
   for nodes in range(len(ishape)):
      dprop = dprop + ' ' + str(ishape[nodes].real) + ',' + str(ishape[nodes].imag)
   ## and close the path
   dprop = dprop + ' ' + str(ishape[0].real) + ',' + str(ishape[0].imag)
   dpaths = parse_path(dprop)
   return dpaths

def maketab(pt1, pt2, orientation):
   # orientation: up=1; down=-1; right=0
   # The assumption is that pt1x < pt2x for top and bottom tabs
   # and pt1y > pt2y for right hand tabs
   tab_height = 0.4
   a = tab_height*math.tan(math.radians(35.0))
   xpt1t = pt1.real + a
   xpt2t = pt2.real - a
   if orientation == 1:
      ypt1t = pt1.imag - tab_height
      ypt2t = pt2.imag - tab_height
   elif orientation == -1:
      ypt1t = pt1.imag + tab_height
      ypt2t = pt2.imag + tab_height
   else:
      if pt1.real == pt2.real:
         # we have a vertical line
         ypt1t = pt1.imag - a
         ypt2t = pt2.imag + a
         xpt1t = pt1.real + tab_height
         xpt2t = pt2.real + tab_height
      else:
         # We need to rotate the points
         m=(pt1.imag-pt2.imag)/(pt1.real-pt2.real)
         msign = (m>0) - (m<0)
         theta = math.atan(m)
         yp1 = (pt1.imag + tab_height) - pt1.imag
         yp2 = (pt2.imag + tab_height) - pt2.imag
         xp1 = xpt1t - pt1.real
         xp2 = xpt2t - pt2.real
         if m > 0:
            # pt1t is rotated theta degrees around pt1
            xpt1t = -xp1*math.cos(theta) + yp1*math.sin(theta) +pt1.real
            ypt1t = -yp1*math.cos(theta) - xp1*math.sin(theta) +pt1.imag
            # pt2t is rotated theta degrees around pt2
            xpt2t = -xp2*math.cos(theta) + yp2*math.sin(theta) +pt2.real
            ypt2t = -yp2*math.cos(theta) - xp2*math.sin(theta) +pt2.imag
         else:
            # pt1t is rotated theta degrees around pt1
            xpt1t = +xp1*math.cos(theta) - yp1*math.sin(theta) +pt1.real
            ypt1t = +yp1*math.cos(theta) + xp1*math.sin(theta) +pt1.imag
            # pt2t is rotated theta degrees around pt2
            xpt2t = xp2*math.cos(theta) - yp2*math.sin(theta) +pt2.real
            ypt2t = +yp2*math.cos(theta) + xp2*math.sin(theta) +pt2.imag
   pt1t = complex(xpt1t, ypt1t)
   pt2t = complex(xpt2t, ypt2t)
   return pt1t, pt2t
# Clean up
if __name__ == "__main__":
   main(sys.argv[1:])# Ensure that arguments are valid
