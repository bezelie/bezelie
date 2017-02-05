# coding:utf-8
import socket
import subprocess
import threading
import picamera
from math import fabs
import re
import os
import binascii
import json
from withings import WithingsAuth, WithingsApi
from pprint import pprint
from  time import sleep
import bezelie
import generatejson
import requests

class MoveThread():
    def __init__(self):        
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target = self.target)
        self.thread.start()

    def target(self):
        while not self.stop_event.is_set():
            bezelie.moveRot (-10)
            bezelie.moveYaw (-40, 4)            
            bezelie.moveRot (10)
            bezelie.moveYaw (40, 4)
            
    def stop(self):
        self.stop_event.set()
        self.thread.join()
    
answer = [u'空いた',\
           u"いくつ",\
           u"食べていい",\
           u"傾向",\
           u"好き",\
           u"体重",\
           u"ベゼリー"
]

#withings key
CONSUMER_KEY = ""

CONSUMER_SECRET = ""

def reAction(question):      
    print question

def getWithingsClient():
    auth = WithingsAuth(CONSUMER_KEY, CONSUMER_SECRET)
    authorize_url = auth.get_authorize_url()
    print "Go to %s allow the app and copy your oauth_verifier" % authorize_url

    oauth_verifier = raw_input('Please enter your oauth_verifier: ')
    creds = auth.get_credentials(oauth_verifier)

    client = WithingsApi(creds)
    return client

def talk(talkword):
    syscom = '/home/pi/bezelie/aquestalkpi/AquesTalkPi -s 120 ' + talkword + ' | sudo  aplay' 
    subprocess.call( syscom , shell=True)
    
def main():

    # TCPクライアントを作成し接続
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 10500))    
    bezelie.centering()
    sf = client.makefile('')
    
    reHungry = re.compile(u'WHYPO WORD="空いた" .* CM="(\d\.\d*)"')
    reHow = re.compile(u'WHYPO WORD="いくつ" .* CM="(\d\.\d*)"')
    reEat = re.compile(u'WHYPO WORD="食べていい" .* CM="(\d\.\d*)"')
    reDir = re.compile(u'WHYPO WORD="傾向" .* CM="(\d\.\d*)"')
    reLove= re.compile(u'WHYPO WORD="好き" .* CM="(\d\.\d*)"')
    reWeight= re.compile(u'WHYPO WORD="体重" .* CM="(\d\.\d*)"')
    reBezelie= re.compile(u'WHYPO WORD="ベゼリー" .* CM="(\d\.\d*)"')
    client = getWithingsClient()
    
    try:
        while True:
            line = sf.readline().decode('utf-8').strip("\n\r")
            word0 = reHungry.search( line )
            word1 = reHow.search( line )
            word2 = reEat.search( line )
            word3 = reDir.search( line )
            word4 = reLove.search( line )
            word5 = reWeight.search( line )
            word6 = reBezelie.search( line )            
            if word0:
                print answer[0]
                if float(word0.group(1)) > 0.9:
                   m = MoveThread()
                   measureGrp = client.get_measures(limit=14)
                   weightRec = 0
                   weightOld = 0
                   for measure in measureGrp:
                       if weightRec == 0:
                           if measure.get_measure(1) :
                               weightRec = measure.get_measure(1)
                       if measure.get_measure(1) :
                            weightOld = measure.get_measure(1)
                   if weightRec > weightOld:
                       talk("体重増え気味だから、我慢しよう")
                   elif weightRec + 1 < weightOld:
                       talk("最近、体重凄く減ってるから無理しすぎないで、ちょっとだけ食べようか")
                   else:
                       talk("安心しちゃダメ、食べたらまた太るよ")
                   sleep(6)
                   m.stop()
            elif word1:
                print answer[1]
                if float(word1.group(1)) > 0.9:
                   with picamera.PiCamera() as camera:
                       camera.resolution = (800, 480)
                       camera.rotation = 180         
                       camera.start_preview()
                       sleep(1)
                       bezelie.centering()
                       talk("どれどれ、写真撮って確認するよ")
                       camera.stop_preview()
                       camera.capture('/home/pi/bezelie/'+ 'detect.jpg')
                       sleep(2)
                       m = MoveThread()
                       recogData = generatejson.imageRecog('image_detect.txt')
                       #you must vision API key 
                       response = requests.post(url='https://vision.googleapis.com/v1/images:annotate?key=',data=recogData,headers={'Content-Type': 'application/json'})                       
                       m.stop()
                       jsondata = json.loads(response.text)
                       print jsondata["responses"][0]["labelAnnotations"][0]["mid"]
                       if jsondata["responses"][0]["labelAnnotations"][0]["mid"] == "/m/06ht1":
                           talk("カップラーメンだね"+"346キロカロリーだよ")
                       else:
                           talk("カロリーメートだね"+"200キロカロリーだよ")
            elif word2:
                print answer[2]
                if float(word2.group(1)) > 0.9:
                   with picamera.PiCamera() as camera:
                       camera.resolution = (800, 480)
                       camera.rotation = 180         
                       camera.start_preview()
                       sleep(1)
                       bezelie.centering()
                       talk("どれどれ、写真撮って確認するよ")
                       camera.stop_preview()
                       camera.capture('/home/pi/bezelie/'+ 'detect.jpg')
                       sleep(2)
                       m = MoveThread()
                       recogData = generatejson.imageRecog('image_detect.txt')
                       #you must vision API key 
                       response = requests.post(url='https://vision.googleapis.com/v1/images:annotate?key=',data=recogData,headers={'Content-Type': 'application/json'})                       
                       m.stop()
                       jsondata = json.loads(response.text)
                       m = MoveThread()
                       measureGrp = client.get_measures(limit=14)
                       weightRec = 0
                       weightOld = 0
                       for measure in measureGrp:
                           if weightRec == 0:
                               if measure.get_measure(1) :
                                   weightRec = measure.get_measure(1)
                           if measure.get_measure(1) :
                               weightOld = measure.get_measure(1)
                       sleep(1)
                       m.stop()
                       if jsondata["responses"][0]["labelAnnotations"][0]["mid"] == "/m/06ht1":
                           if weightRec > weightOld:
                               talk("体重が増加傾向にあるのにカップラーメン食べちゃダメだよ")
                           else:
                               talk("体重は減少傾向だけど、カップラーメン食べすぎないほうがいいんじゃないかな")
                       else:
                           if weightRec > weightOld:
                               talk("体重が増加傾向だけど、カロリーメートで少し不足分を補ったほうがいいかもね")
                           else:
                               talk("体重が減少傾向だね、カロリーメートぐらいなら大丈夫かもね")                           
            elif word3:
                print answer[3]
                if float(word3.group(1)) > 0.9:                   
                   m = MoveThread()
                   measureGrp = client.get_measures(limit=14)
                   weightRec = 0
                   weightOld = 0
                   for measure in measureGrp:
                       if weightRec == 0:
                           if measure.get_measure(1) :
                               weightRec = measure.get_measure(1)
                       if measure.get_measure(1) :
                           weightOld = measure.get_measure(1)
                   sleep(1)
                   m.stop()
                   diff = fabs(weightRec - weightOld)
                   if weightRec > weightOld :
                       talk("体重一週間前よりも" + str(diff)+ "kg増え気味だね")
                   else:
                       talk("体重一週間前よりも" + str(diff)+ "kg減ってるね") 
            elif word4:
                print answer[4]
                if float(word4.group(1)) > 0.9:                    
                    talk("ありがとう、僕も好きだよ")

            elif word5:
                print answer[5]
                if float(word5.group(1)) > 0.9:
                   m = MoveThread()
                   measureGrp = client.get_measures(limit=14)
                   weightRec = 0
                   weightOld = 0
                   for measure in measureGrp:
                       if weightRec == 0:
                           if measure.get_measure(1) :
                               weightRec = measure.get_measure(1)
                       if measure.get_measure(1) :
                            weightOld = measure.get_measure(1)
                   sleep(2)
                   m.stop()
                   talk("現在"+str(weightRec)+"kgだね")
                   sleep(1)
                   talk("ちなみに、僕の体重はりんご一個分だよ")
            elif word6:
                print answer[6]
                if float(word6.group(1)) > 0.9:
                    random128bitdata = os.urandom(16)
                    if int(binascii.hexlify(random128bitdata),16)%2 == 0:
                        talk("どうしたの")
                    else:
                        talk("なーにー")
            else:
                pass
    except KeyboardInterrupt:
        print "KeyboardInterrupt occured."
        client.close()        
        
if __name__ == "__main__":
    main()
