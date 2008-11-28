"""
Utility functions to support the Echo Nest web API interface.  This
module is not meant for other uses and should not be used unless
modifying or extending the package.
"""

__version__ = "$Revision: 0 $"
# $Source$

# Standard packages.
import httplib
import mimetypes
import urllib
import xml.dom.minidom

# Nonstandard packages.
import echonest.web.config as config


SUCCESS_STATUS_CODES = ( 0, )


def apiFunctionPrototype( method, id) : 
    """
    This function is the basis for most of the 'get_xxx' functions in
    this package.
    """
    # Check if ID is an MD5 string, if so, use that instead of ID.
    if(len(id)<32):
        params = urllib.urlencode({'id': id, 'api_key': config.API_KEY})
    else:
        params = urllib.urlencode({'md5': id, 'api_key': config.API_KEY})
    url = 'http://%s%s%s?%s' % (config.API_HOST, config.API_SELECTOR, method, params)
    f = urllib.urlopen( url )
    return parseXMLString(f.read())



def parseXMLString( xmlString ) :
    """
    This function is meant to modularize the handling of XML strings
    returned by the web API.  Overriding this method will change how
    the entire package parses XML strings.

    @param xmlString The plaintext string of XML to parse.

    @return An object representation of the XML string, in this case a
    xml.dom.minidom representation.
    """
    doc = xml.dom.minidom.parseString(xmlString)
    status_code = int(doc.getElementsByTagName('code')[0].firstChild.data)
    if status_code not in SUCCESS_STATUS_CODES :
        status_message = doc.getElementsByTagName('message')[0].firstChild.data
        raise Exception('Echo Nest API Error %d: %s' % (status_code, status_message) )
    return doc



def postMultipart(host, selector, fields, files):
    """
    Adapted from http://code.activestate.com/recipes/146306/ .

    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encodeMultipartFormdata(fields, files)
    h = httplib.HTTPConnection(host)
    headers = { 'User-Agent': config.HTTP_USER_AGENT,
                'Content-Type': content_type }
    h.request('POST', selector, body, headers)
    res = h.getresponse()
    return res.status, res.reason, res.read()



def encodeMultipartFormdata(fields, files):
    """
    Adapted from http://code.activestate.com/recipes/146306/ .

    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------------------------9bab5c68ca11'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % getContentType(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body



def getContentType(filename):
    """
    Adapted from http://code.activestate.com/recipes/146306/ .
    """
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
