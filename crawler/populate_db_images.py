from os import listdir
from os.path import isfile, join

mypath = "crawler/images/"
# onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
onlyfiles = ['930102.jpg', '010012.jpg', '530403.jpg', '300231.jpg', '320202.jpg', '110102.jpg', '050271.jpg', '050332.jpg', '210342.jpg', '500232.jpg', '210212.jpg', '520311.jpg', '020088.jpg', '110112.jpg', '100471.jpg', '041211.jpg', '520332.jpg', '560232.jpg', 'aps081.jpg', '300472.jpg', '350102.jpg', '530432.jpg', '520102.jpg', '420482.jpg', '051462.jpg', '900561.jpg', 'aps031.jpg', '110262.jpg', '320584.jpg', '120102.jpg', '940101.jpg', '200212.jpg', '400262.jpg', '300342.jpg', '300452.jpg', 'aps052.jpg', '400232.jpg', '041201.jpg', '320232.jpg', '320691.jpg', '520212.jpg', '050252.jpg', '020090.jpg', '040122.jpg', '051444.jpg', '300541.jpg', '720302.jpg', '040102.jpg', '520252.jpg', '120202.jpg', '530601.jpg', '300202.jpg', '300432.jpg', '051432.jpg', '011004.jpg', '990202.jpg', '051454.jpg', '320411.jpg', '100212.jpg', '020087.jpg', '300551.jpg', '640201.jpg', '020077.jpg', '320533.jpg', '560202.jpg', '400112.jpg', '300362.jpg', '990222.jpg', '300102.jpg', '032112.jpg', '011010.jpg', '051452.jpg', '701201.jpg', '400222.jpg', '900452.jpg', '051402.jpg', '530532.jpg', '200422.jpg', '210202.jpg', '210222.jpg', 'aps026.jpg', '420441.jpg', '050232.jpg', '520342.jpg', '400132.jpg', '520202.jpg', '110361.jpg', '210112.jpg', '320591.jpg', '013002.jpg', '500222.jpg', '560112.jpg', '500112.jpg', '051414.jpg', '200331.jpg', 'aps049.jpg', '200232.jpg', '530474.jpg', '530591.jpg', '040322.jpg', 'aps142.jpg', '013001.jpg', '020076.jpg', '530611.jpg', 'aps033.jpg', '930221.jpg', '080202.jpg', '210241.jpg', '210102.jpg', '530621.jpg', '210111.jpg', '400322.jpg', '530482.jpg', '100392.jpg', '001102.jpg', '930351.jpg', 'aps084.jpg', '320581.jpg', '300112.jpg', '520232.jpg', '930361.jpg', '350112.jpg', '200102.jpg', '300422.jpg', '320222.jpg', '420412.jpg', '930302.jpg', '011002.jpg', '211301.jpg', '320622.jpg', '730202.jpg', '001121.jpg', '032301.jpg', '400121.jpg', '420471.jpg', '001162.jpg', '990121.jpg', '900502.jpg', '320621.jpg', '930241.jpg', '990402.jpg', 'aps023.jpg', '200302.jpg', '200432.jpg', '710211.jpg', '012002.jpg', '420462.jpg', '300462.jpg', '100552.jpg', '400302.jpg', '050112.jpg', '050221.jpg', '400103.jpg', '300332.jpg', 'aps083.jpg', '900541.jpg', '210382.jpg', '320352.jpg', 'aps013.jpg', '200103.jpg', '320681.jpg', '560122.jpg', 'aps051.jpg', '850202.jpg', '400212.jpg', '300322.jpg', '040211.jpg', '201231.jpg', '300212.jpg', '210302.jpg', '200222.jpg', '420522.jpg', '300441.jpg', '560332.jpg', '010020.jpg', '050212.jpg', '200112.jpg', '560302.jpg', '100472.jpg', '010004.jpg', '530402.jpg', '710302.jpg', '520112.jpg', '320541.jpg', '051411.jpg', '011026.jpg', '051541.jpg', '400342.jpg', '020089.jpg', '530581.jpg', '550321.jpg', '320564.jpg', '080222.jpg', 'aps117.jpg', '201322.jpg', '041202.jpg', '320212.jpg', '920112.jpg', '051434.jpg', '050102.jpg', '011016.jpg', '730102.jpg', '012012.jpg', '051472.jpg', '010002.jpg', '100431.jpg', '001152.jpg', '012006.jpg', '710101.jpg', '032102.jpg', 'aps141.jpg', 'aps123.jpg', '400332.jpg', '720201.jpg', '100412.jpg', '930352.jpg', '850322.jpg', '320342.jpg', '210232.jpg', '560212.jpg', '200321.jpg', '200471.jpg', '050322.jpg', '940201.jpg', '010016.jpg', '210352.jpg', '420431.jpg', '970152.jpg', '320523.jpg', '530642.jpg', '320671.jpg', '011008.jpg', '110231.jpg', 'aps039.jpg', '300412.jpg', '120212.jpg', '320554.jpg', '011014.jpg', '560312.jpg', '080212.jpg', '500201.jpg', '320534.jpg', 'aps032.jpg', '200202.jpg', '110512.jpg', '100353.jpg', '320102.jpg', '110392.jpg', '500122.jpg', '300482.jpg', '970202.jpg', '500362.jpg', '001132.jpg', '040362.jpg', '850201.jpg', '520362.jpg', '010006.jpg', '990102.jpg', '100421.jpg', '300222.jpg', '001172.jpg', '640212.jpg', '051442.jpg', '320142.jpg', '011012.jpg', '300471.jpg', '320312.jpg', '001112.jpg', 'aps048.jpg', '400912.jpg', '300442.jpg', '020091.jpg', '052102.jpg', '010024.jpg', '012004.jpg', '100292.jpg', '560322.jpg', '520302.jpg', '500321.jpg', '200322.jpg', 'aps126.jpg', '530631.jpg', '320112.jpg', '010010.jpg', '910202.jpg', '930101.jpg', '300302.jpg', '701202.jpg', 'aps050.jpg', '010014.jpg', '010008.jpg', '840202.jpg', '530421.jpg', '100522.jpg', '120112.jpg', 'aps067.jpg', '930312.jpg']
filepaths = [mypath + f for f in onlyfiles]

from app.models import *
from django.core.files import File
import time

for filepath in filepaths:
    cid = filepath.replace('.jpg','').replace(mypath, '')
    print cid
    course = Course.objects.filter(course_id = cid)
    if len(course) == 1:
        course = course[0]
        if not course.image:
            f = open(filepath)
            myf = File(f)
            course.image = myf
            course.save()
    else:
        print "Error! There were more files with that ID!"

        