""" stupidxml - A library for simple xml generation

Author: Justin Driscoll <http://justindriscoll.us>

Copyright (c) 2007, Justin C. Driscoll
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of django-photologue nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
from xml.dom.minidom import parseString
from xml.sax.saxutils import escape


class AttributeDict(dict):
    """ Simple dict subclass to allow dot notation assignment on attributes """
    def __setattr__(self, name, value):
        if value is None:
            del self[name]
        else:
            self[name] = value


class Node(object):
    """ Object representation of an XML node

    A Nestable XML node class. Contents can be any object with
    a __str__ method.

    >>> root = Node("root")
    >>> str(root)
    '<root />'

    >>> project = root.append(Node("project", copyright="2008"))
    >>> str(root)
    '<root><project copyright="2008" /></root>'

    >>> project.attributes.language = "Python"
    >>> str(root)
    '<root><project language="Python" copyright="2008" /></root>'

    >>> name = Node("name", "StupidXML")
    >>> author = Node("author", "Justin Driscoll", href="http://justindriscoll.us")
    >>> project.append([name, author])
    [<StupidXML.Node: "name">, <StupidXML.Node: "author">]

    >>> str(project)
    '<project language="Python" copyright="2008"><name>StupidXML</name><author href="http://justindriscoll.us">Justin Driscoll</author></project>'

    >>> str(root)
    '<root><project language="Python" copyright="2008"><name>StupidXML</name><author href="http://justindriscoll.us">Justin Driscoll</author></project></root>'

    """
    def __init__(self, tagname, contents=None, attributes=None, **kwargs):
        self.tagname = tagname
        self.contents = []
        self.append(contents)
        self.attributes = AttributeDict()
        if attributes is not None:
            kwargs.update(attributes)
        for name, value in kwargs.items():
            self.attributes[name] = value
    
    def __repr__(self):
        return '<StupidXML.Node: "%s">' % self.tagname
    
    def __str__(self):
        if not len(self.contents):
            return "<%s%s />" % (self.tagname, self.attributes_to_str())
        else:
            return "<%s%s>%s</%s>" % (self.tagname,
                                      self.attributes_to_str(),
                                      "".join([str(node) for node \
                                               in self.contents]),
                                      self.tagname)
    
    @property
    def dom(self):
        return parseString(self.__str__())
    
    def append(self, contents=None):
        if contents is not None:
            if self.is_iterable(contents):
                self.contents.extend(list(contents))
            else:
                self.contents.append(contents)
        return contents
    
    def is_iterable(self, obj):
        if isinstance(obj, basestring): return False
        try: iter(obj)
        except: return False
        else: return True
    
    def attributes_to_str(self):
        return "".join([' %s="%s"' % (key, escape(str(value))) \
                        for key, value in self.attributes.items()])


class HTMLNode(Node):
    """ HTML 4 compliant Node

    Node renders as standard HTML 4 markup.

    >>> br = HTMLNode("br")
    >>> str(br)
    '<br>'
    >>> img = HTMLNode("img", src="http://domain.com/image.jpg")
    >>> str(img)
    '<img src="http://domain.com/image.jpg">'
    >>> p = HTMLNode("p")
    >>> p.append(img)
    <StupidXML.HTMLNode: "img">
    >>> str(p)
    '<p><img src="http://domain.com/image.jpg"></p>'

    """
    EMPTY_TAGS = ("area", "base", "basefont", "br", "col",
                  "frame", "hr", "img", "input", "isindex",
                  "link", "meta", "param")

    def __str__(self):
        if self.tagname in self.EMPTY_TAGS:
            return "<%s%s>" % (self.tagname, self.attributes_to_str())
        else:
            return "<%s%s>%s</%s>" % (self.tagname,
                                      self.attributes_to_str(),
                                      "".join([str(node) for node \
                                               in self.contents]),
                                      self.tagname)

    def __repr__(self):
        return '<StupidXML.HTMLNode: "%s">' % self.tagname

    def append(self, contents=None):
        if contents is not None and self.tagname in self.EMPTY_TAGS:
            raise ValueError("Empty HTML tags do accept contents. See HTMLNode.EMPTY_TAGS for a complete list.")
        return super(HTMLNode, self).append(contents)