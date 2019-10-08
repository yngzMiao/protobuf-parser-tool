# -*- coding:UTF-8 -*-

import sys
sys.path.append("../")
import struct
import logging
logging.basicConfig(level=logging.DEBUG)
from google.protobuf.descriptor import FieldDescriptor as FD
import simplejson


class GeneralProtoReader:
  # Initialize reader, need assign class_name
  def __init__(self, protofile, proto):
    self._index = 0
    self.IndexHeader = [0]
    self.IndexLength = [4]
    self.hasProto = False
    self.protofile = open(str(protofile),"rb")
    self.proto = proto()
    self.version = self.parseBindata(self.protofile.read(4))
    self.createIndex()

  # Get version information
  def getVersion(self):
    return self.version

  # Stop Reader
  def stopReader(self):
    self.protofile.close()
  
  # Get the proto buffer data of the index frame
  def setFrameIndex(self, index):
    if index >= self.getFrameCount() or index < 0:
      logging.fatal("[Attention] : setFrameIndex() >> index is out of range.")
      self.hasProto = False
      return None

    self._index = index
    self.hasProto = True
    self.protofile.seek(self.IndexHeader[index])
    data = self.protofile.read(self.IndexLength[index])
    self.proto.ParseFromString(data)
    return self.proto

  # Query statement stitching interface
  def catenate(*args):
    s = ''
    for v in args:
      if v is None or not isinstance(v, basestring):
        continue
      s += (('.' + v) if len(s) > 0 else v)
    return s

  # General sigle query interface for proto
  def getFrameData_general(self, *args):
    if not self.hasProto:
      logging.fatal("[Attention] : getFrameData_general() >> need setFrameIndex() before.")
      return None
    try:
      return eval(self.catenate('self.proto', *args))
    except:
      return None

  # General batch query interface for proto
  def getFrameData_general_arr(self, field, *args):
    if not self.hasProto:
      logging.fatal("[Attention] : getFrameData_general_arr() >> need setFrameIndex() before.")
      return None
    try:
      arr = eval(self.catenate('self.proto', *args))
      if field is None:
        return arr
      ret = []
      for v in arr:
        ret.append(eval(self.catenate('v', field)))
      return ret
    except:
      return None

  # Get total proto frame count
  def getFrameCount(self):
    return min(len(self.IndexHeader),len(self.IndexLength))

  # Parsing 4 Byte binary data
  def parseBindata(self,temp_len):
    binval = [int(struct.unpack('b', temp_len[0])[0]),
              int(struct.unpack('b', temp_len[1])[0]),
              int(struct.unpack('b', temp_len[2])[0]),
              int(struct.unpack('b', temp_len[3])[0])]
    re = (binval[0] << 24) & 0xFF000000
    re = ((binval[1] << 16) & 0x00FF0000) | re
    re = ((binval[2] << 8) & 0x0000FF00) | re
    re = ((binval[3]) & 0x000000FF) | re
    return re

  # Create index dictionary
  def createIndex(self):
    while True:
      try:
        aftersize = self.parseBindata(self.protofile.read(4))
        self.IndexHeader.append(self.IndexHeader[-1] + self.IndexLength[-1] + 4)
        self.IndexLength.append(aftersize)
        self.protofile.seek(aftersize,1)
      except:
        break
    self.IndexHeader = self.IndexHeader[1:]
    self.IndexLength = self.IndexLength[1:]

  # Get frame proto data in json format
  def getFrameData_json(self):
    if not self.hasProto:
      logging.fatal("[Attention] : getFrameData_json() >> need setFrameIndex() before.")
      return None 
    return simplejson.dumps(self.pb2dict(self.proto))
  
  # Convert proto data to dict
  def pb2dict(self, obj):
    adict = {}
    if not obj.IsInitialized():
      return None
    for field in obj.DESCRIPTOR.fields:
      if not getattr(obj, field.name):
        continue
      if not field.label == FD.LABEL_REPEATED:
        if not field.type == FD.TYPE_MESSAGE:
          adict[field.name] = getattr(obj, field.name)
        else:
          value = self.pb2dict(getattr(obj, field.name))
          if value:
            adict[field.name] = value
      else:
        if field.type == FD.TYPE_MESSAGE:
          adict[field.name] = [self.pb2dict(v) for v in getattr(obj, field.name)]
        else:
          adict[field.name] = [v for v in getattr(obj, field.name)]
    return adict

if __name__ == "__main__":
  pass