import eyeD3, os, os.path, MySQLdb, pickle, re, S3local, simplejson, sqs, tempfile, time, urllib
from cowbell import Cowbell
from xml.dom.minidom import parseString

API_ENDPOINT = 'http://analyzeendpoint.echonest.com/analyze/endpoint.py/'

AWS_ACCESS = '1893Q8H967CXVDD6H702'
AWS_SECRET = 'u00ve9U5XlAufz+JmHmFV87B5uq4LULvSu2gIQuJ'

SQS_QUEUE = 'cowbell'

S3_ACL = '<?xml version="1.0" encoding="UTF-8"?>\n<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Owner><ID>22eeb63957386eeb3953bc503e9023b4dc04831296401e33bb141dd43cecfaa6</ID><DisplayName>thesupermusic</DisplayName></Owner><AccessControlList><Grant><Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser"><ID>22eeb63957386eeb3953bc503e9023b4dc04831296401e33bb141dd43cecfaa6</ID><DisplayName>thesupermusic</DisplayName></Grantee><Permission>FULL_CONTROL</Permission></Grant><Grant><Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="Group"><URI>http://acs.amazonaws.com/groups/global/AllUsers</URI></Grantee><Permission>READ</Permission></Grant></AccessControlList></AccessControlPolicy>'
S3_UPLOAD = 'cowbell-upload'
S3_PUBLIC = 'cowbell'

DATABASE_NAME = 'cowbell'
DATABASE_USER = 'nest'
DATABASE_PASSWORD = 'kittycat'
DATABASE_HOST = '72.249.85.6'

def status_code(doc):
    return doc.firstChild.firstChild.firstChild.firstChild.data

def S3_upload(key, value):
    conn = S3local.AWSAuthConnection(AWS_ACCESS, AWS_SECRET)
    
    conn.put(S3_PUBLIC, key, value)
    conn.put_acl(S3_PUBLIC, key, S3_ACL)

class Worker:
    def read_queue(self):
        t1 = time.time()

        try:
            s = sqs.SQSService(AWS_ACCESS, AWS_SECRET)
            q = s.get(SQS_QUEUE)
            m = q.read()
        
            if m is not None:
                params = simplejson.loads(m.body)
                q.delete(m)
                
                self.id = params['id']
                self.S3_key = params['S3_key']
                self.cowbell_intensity = params['cowbell_intensity']
                self.walken_intensity = params['walken_intensity']
                
                print 'read_queue(): %g\n%self' % (time.time() - t1, params)
                return True
            else:
                return False
        except:
            return False

    def upload(self, call_count=0):
        t1 = time.time()
        print "u1"
        try:
            url = urllib.urlopen('%supload?api_key=cowbell&wait=y&url=http://%s.s3.amazonaws.com/%s' % (API_ENDPOINT, S3_UPLOAD, self.S3_key.replace(' ', '+')))
            response = parseString(url.read())
            url.close()
            
            code = status_code(response)
        except:
            print 'upload(): exception trying to load xml'
            return False
        print "u2"
        
        # success
        if code == '0':
            self.thingID = response.firstChild.childNodes[2].firstChild.data
            print self.thingID
            print 'upload(): %g' % (time.time() - t1)
            return True

        
        # still processing
        elif code == '5':
            if call_count < 3:
                time.sleep(10)
                return self.upload(call_count + 1)
            else:
                print 'upload(): analysis not ready after 30s'
                return False
        
        # other errors
        else:
            print 'upload(): error %s' % code
            return False

    def read_analysis(self, method):
        url = urllib.urlopen('%sanalysis?thingID=%s&method=%s' % (API_ENDPOINT, self.thingID, method))
        response = parseString(url.read())
        url.close()
        
        return response

    def read_beats(self):
        t1 = time.time()
        print "READ BEATS"
        try:
            response = self.read_analysis('beats')
        except:
            print 'read_beats(): exception trying to load xml'
            return False
        
        if status_code(response) == '0':
            num_beats = len(response.firstChild.childNodes[3].childNodes)

            self.beats = []
            for i in range(num_beats):
                start = float(response.firstChild.childNodes[3].childNodes[i].firstChild.data)

                self.beats.append({'start': start})
                self.beats[i - 1]['duration'] = start - self.beats[i - 1]['start']

            self.beats[num_beats - 1]['duration'] = self.beats[num_beats - 2]['duration']
            
            print 'read_beats(): %g' % (time.time() - t1)
            return True
        else:
            print 'read_beats(): error'
            return False

    def read_sections(self):
        print "READ SECTIONS"
        t1 = time.time()
        
        try:
            response = self.read_analysis('sections')
        except:
            print 'read_sections(): exception trying to load xml'
            return False
        
        if status_code(response) == '0':
            self.sections = []
            for node in response.firstChild.childNodes[3].childNodes:
                self.sections.append(float(node.getAttribute('start')))
            
            print 'read_sections(): %g' % (time.time() - t1)
            return True
        else:
            print 'read_sections(): error'
            return False

    def read_metadata(self):
        t1 = time.time()
        
        self.metadata = {}
        try:
            response = self.read_analysis('metadata')
        except:
            print 'read_metadata(): exception trying to load xml'
            return False
        
        if status_code(response) == '0':
            for node in response.firstChild.childNodes[3].childNodes:
                self.metadata[node.nodeName] = node.firstChild.data
            
            print 'read_metadata(): %g' % (time.time() - t1)
        else:
            print 'read_metadata(): error'
        
        return True

    def mp3_path(self):
        handle, path = tempfile.mkstemp('.mp3')
        
        mp3 = open(path, 'w+b')
        mp3.write(urllib.urlopen('http://%s.s3.amazonaws.com/%s' % (S3_UPLOAD, self.S3_key.replace(' ', '+'))).read())
        mp3.flush()
        mp3.close()
        
        return path

    def write_tags(self, path):
        t1 = time.time()
        
        try:
            tag = eyeD3.Tag()
            tag.link(path)
            tag.header.setVersion(eyeD3.ID3_V2_3)
            
            if self.metadata.has_key('artist'):
                tag.setArtist(self.metadata['artist'])
                self.db_cursor.execute('UPDATE create_track SET id3_artist = "%s" WHERE name = "%s"' % (self.metadata['artist'], self.id))
            if self.metadata.has_key('release'):
                tag.setAlbum(self.metadata['release'])
                self.db_cursor.execute('UPDATE create_track SET id3_release = "%s" WHERE name = "%s"' % (self.metadata['release'], self.id))
            if self.metadata.has_key('title'):
                tag.setTitle(self.metadata['title'])
                self.db_cursor.execute('UPDATE create_track SET id3_title = "%s" WHERE name = "%s"' % (self.metadata['title'], self.id))
            else:
                tag.setTitle('Unknown song')
                self.db_cursor.execute('UPDATE create_track SET id3_title = "Unknown song" WHERE name = "%s"' % (self.id))
            
            tag.update()
            
            print 'write_tags(): %g' % (time.time() - t1)
        except:
            print 'write_tags(): exception while writing tags'

    def run(self):
        if self.read_queue():
            s3 = S3local.AWSAuthConnection(AWS_ACCESS, AWS_SECRET)
            print "1"
            self.db = MySQLdb.Connect(host=DATABASE_HOST, port=3306, user=DATABASE_USER, passwd=DATABASE_PASSWORD, db=DATABASE_NAME)
            print "2"
            self.db_cursor = self.db.cursor()
            print "3"
            if self.upload() and self.read_beats() and self.read_sections() and self.read_metadata():
                print "4"
                # render MP3
                mp3_path = self.mp3_path()
                print "4.5"
                output_path = Cowbell(mp3_path, self.beats, self.sections).run(self.cowbell_intensity, self.walken_intensity)
                print "4.6"
                self.write_tags(output_path)
                print "5"
                # copy MP3 to S3
                output = open(output_path, 'rb')
                print "6"
                s3.put(S3_PUBLIC, self.id + '.mp3', output.read())
                print "7"
                s3.put_acl(S3_PUBLIC, self.id + '.mp3', S3_ACL)
                print "8"
                output.close()
                print "9"
                # remove temp files
                os.remove(mp3_path)
                print "10"
                os.remove(output_path)
                print "11"
                # update stored metadata
                self.db_cursor.execute('UPDATE create_track SET rendered = NOW(), status = "Y", thingID = "%s" WHERE name = "%s"' % (self.thingID, self.id))
                print "12"
            else:
                print "3,5"
                self.db_cursor.execute('UPDATE create_track SET status = "N" WHERE name = "%s"' % self.id)
                print "3.6"
            print "13"
            # delete uploaded MP3
            s3.delete(S3_UPLOAD, self.S3_key)
            
            self.db.close()

if __name__ == '__main__':
    while True:
        Worker().run()
        time.sleep(1)
