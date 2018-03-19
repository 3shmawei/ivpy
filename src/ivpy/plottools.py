from PIL import Image,ImageDraw,ImageFont
from numpy import repeat,radians,cos,sin
from math import ceil

def _gridcoords(n,ncols,thumb):
    nrows = int( ceil( float(n) / ncols ) ) # final row may be incomplete
    w,h = ncols*thumb,nrows*thumb

    xgrid = range(ncols) * nrows
    ygrid = repeat(range(nrows),ncols)
    xgrid = xgrid[:n]
    ygrid = ygrid[:n]
    x = [item*thumb for item in xgrid]
    y = [item*thumb for item in ygrid]

    return w,h,zip(x,y)

def _gridcoordscirclemax(side,thumb):
    x,y = range(side)*side,repeat(range(side),side)
    gridlist = [Point(item) for item in zip(x,y)]
    maximus = Point(side/2,side/2)
    return gridlist,maximus,[(int(maximus.x*thumb),int(maximus.y*thumb))]

def _gridcoordscircle(n,maximus,gridlist,thumb):
    # compute distances from center; sort by distance
    dists = [maximus.distance(item) for item in gridlist]
    tmp = pd.DataFrame({"gridlist":gridlist,"dists":dists})
    tmp.sort_values(by='dists',inplace=True) # ascending
    gridlist = tmp.gridlist.iloc[:n-1] # n-1 bc we removed maximus
    return [(int(item.x*thumb),int(item.y*thumb)) for item in gridlist]

def _pol2cart((rho,phi)):
    x = rho * cos(phi)
    y = rho * sin(phi)
    return(x,y)

def _bin2phi(nbins,binnum):
    incr = float(360)/nbins
    return radians(incr*binnum)

def _bin2phideg(nbins,binnum):
    incr = float(360)/nbins
    return incr*binnum

def _histcoordscart(n,binlabel,plotheight,thumb):
    xcoord = thumb * binlabel
    ycoord = plotheight - thumb # bc paste loc is UPPER left corner
    ycoords = arange(ycoord,plotheight-thumb*(n+1),-thumb)
    return [tuple((xcoord,item)) for item in ycoords]

def _histcoordspolar(n,binlabel,binmax,nbins,thumb):
    rhos = arange(binmax,binmax-n-1,-1)
    phi = _bin2phi(nbins,binlabel)
    phis = repeat(_bin2phideg(nbins,binlabel),n)
    xycoords = [_pol2cart((rho,phi)) for rho in rhos]
    x = [int((item[0]+binmax)*thumb) for item in xycoords]
    y = [int((binmax-item[1])*thumb) for item in xycoords]
    return zip(x,y)

def _scalecart(featcol,ycol,xdomain,ydomain,side,thumb):
    featcolpct = _pct(featcol,xdomain)
    ycolpct = _pct(ycol,ydomain)
    pasterange = side - thumb # otherwise will cut off extremes
    x = [int(item*pasterange) for item in featcolpct]
    y = [int((1-item)*pasterange) for item in ycolpct]
    return x,y

def _scalepol(featcol,ycol,xdomain,ydomain,side,thumb):
    # get percentiles for col values
    featcolpct = _pct(featcol,xdomain)
    ycolpct = _pct(ycol,ydomain)
    # derive polar coordinates from percentiles and 360 degree std
    rhos = [item for item in featcolpct] # unit radius
    phis = [item*float(360) for item in ycolpct]
    phiradians = [radians(item) for item in phis]
    # convert these to xy coordinates in (-1,1) range
    xycoords = [_pol2cart(item) for item in zip(rhos,phiradians)]
    # convert to canvas coordinates
    pasterange = side - thumb # otherwise will cut off extremes
    radius = float(pasterange)/2
    x = [int(item[0]*radius+radius) for item in xycoords]
    y = [int(radius-item[1]*radius) for item in xycoords]
    return x,y,phis

def _pct(col,domain):
    """This will fail on missing data"""
    if domain==None:
        dmin = col.min()
        dmax = col.max()
    else:
        # if we contract domain, this is equivalent to above
        dmin = domain[0]
        dmax = domain[1]
    drange = dmax - dmin
    return [(item - dmin) / float(drange) for item in col]

def _idx(im,i):
    pos = 0 # hard-code
    draw = ImageDraw.Draw(im)
    text = str(int(i))
    font = ImageFont.truetype('../fonts/VeraMono.ttf', 8)
    fontWidth, fontHeight = font.getsize(text)

    try:
        draw.rectangle(
            [(pos,pos),(pos+fontWidth,pos+fontHeight)],
            fill='#282828',
            outline=None
        )

        draw.text((pos,pos),text,font=font,fill='#efefef')

    except Exception as e:
        print e

def _placeholder(thumb):
    im = Image.new('RGB',(thumb,thumb),'#969696')
    draw = ImageDraw.Draw(im)
    draw.line([(0,0),(thumb,thumb)],'#dddddd')
    return im

def _paste(pathcol,thumb,idx,canvas,coords,coordinates=None,phis=None):
    counter=-1
    for i in pathcol.index:
        counter+=1
        try:
            im = Image.open(pathcol.loc[i])
        except:
            im = _placeholder(thumb)
        im.thumbnail((thumb,thumb),Image.ANTIALIAS)
        if idx==True: # idx labels placed after thumbnail
            _idx(im,i)
        if coordinates=='polar':
            phi = phis[counter]
            if 90 < phi < 270:
                phi = phi + 180 # avoids upside down images
            im = im.convert('RGBA') # need alpha layer to make rotation work
            im = im.rotate(phi,expand=1) # expand so it won't clip the corners
            canvas.paste(im,coords[counter],im) # im is a mask for itself
        else:
            canvas.paste(im,coords[counter])

def _round(x,direction='down'):
    if direction=='down':
        return int(x)
    elif direction=='up':
        return int(ceil(x)) # ceil returns float

def _getsizes(args):
    plotsizes = [item.size for item in args]
    return [item for sublist in plotsizes for item in sublist]
