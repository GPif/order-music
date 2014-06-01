#!/usr/bin/python

import os
from optparse import OptionParser #Optioin parse lib
from unidecode import unidecode
import re #For regex
import shutil
import eyed3 #mp3 id3 tag handeler lib

def list_file(d):
  flist=[]
  for (dirname,subher,fileshere) in os.walk(u'%s'% (d)):
    for fname in fileshere:
      fpath = os.path.join( dirname , fname )
      flist.append(fpath)
  return flist

def split_list(l,f):
  filtred = []
  remain = []
  for elt in l:
    if (f(elt)):
      filtred.append(elt)
    else:
      remain.append(elt)
  return ( filtred , remain )

#Copy file, add a number if the file already exists
def my_copy(source,dest):
  nb=1
  if not os.path.exists(dest):
    shutil.copy (source, dest)
  else:
    while (os.path.exists("%s(%d)" % (dest,nb))):
      nb +=1
    shutil.copy (source, "%s(%d)" % (dest,nb))

def store_in(lt,folder):
  outdir = os.path.join(folder)
  if not os.path.exists(outdir):
    os.makedirs(outdir)
  for elt in lt:
    my_copy(elt,os.path.join(outdir,os.path.basename(elt)))

def get_mp3_tag(_file):
  f=eyed3.load(_file)
  tag = dict(
	artist=f.tag.artist,
	album=f.tag.album,
	title=f.tag.title,
	track=int(f.tag.track_num[0])
  )
  return tag

#is file ok
def is_mp3_ok(mp3f):
  mp3inf = get_mp3_tag(mp3f)
  for k in mp3inf:
    if (not mp3inf[k]):
      print ('%s Not correct mp3 %s is missing' % (mp3f,k))
      return False
    if (not isinstance(mp3inf['track'], int)):
      print ('%s the track is not an integer' % (mp3f))
      return False
  return True

def clean_string(_str):
    _str=unidecode(_str)
    _str=re.sub('[^\sA-Za-z0-9]','',_str)
    _str=re.sub(r'\s', "_",_str)
    return _str

#treat each mp3 file
def gen_mp3_path(mp3):
  mp3inf = get_mp3_tag(mp3)
  #prepare output file name
  title=clean_string(mp3inf['title'])
  artist=clean_string(mp3inf['artist'])
  album=clean_string(mp3inf['album'])
  out_file="%02d-%s.mp3" % (int(mp3inf['track']),title.lower())
  directory="%s/%s" % (artist,album)
  #create directory
  #print ("out_file: %s directory:%s",out_file,directory)
  return (out_file,directory)

#option part to control input
#return : option dict and arguments
def opt_parse():
  parser = OptionParser(usage="usage: %prog dirpath",
    version="%prog 1.0")

  parser.add_option("-o", "--output",
                  action="store",
                  type="string",
                  dest="output",
                  default=".",
		  help="Output directory"
                  )

  (options, args) = parser.parse_args()

  if len(args) != 1:
    parser.debug("wrong number of arguments")
  return (options, args)

#Main part run to store my mp3 collection
if __name__ == '__main__':
  (gopt,argv)=opt_parse()
  l = list_file(argv[0])

  #Remove no mp3 file
  def f(x): return x.endswith('mp3')
  (q,r) = split_list(l,f)

  #List ok and ko mp3
  (ok_l,ko_l) = split_list(q,is_mp3_ok)

  store_in(r,gopt.output+'/_trash')
  store_in(ko_l,gopt.output+'/ko_mp3')

  for elt in ok_l:
    ( fname , fpath ) = gen_mp3_path(elt)
    print "%s : %s" % ( fname , fpath )
    if not os.path.exists(gopt.output+'/'+fpath):
      os.makedirs(gopt.output+'/'+fpath)
    my_copy ( elt , gopt.output+'/'+fpath+'/'+fname )
