# -*- coding:UTF-8 -*-

import sys
sys.path.append("../")
import struct
import logging
logging.basicConfig(level=logging.DEBUG)
from google.protobuf.descriptor import FieldDescriptor as FD
import simplejson


class ConvertException(Exception):
  pass

class GeneralProtoWriter:
  def __init__(self, protofile, proto, version=20191001):
    self.protofile = open(str(protofile),"wb")
    self.writeVersion(int(version))
    self.proto = proto

  # Stop Writer
  def stopWriter(self):
    self.protofile.close()

  # Write version into proto
  def writeVersion(self, version):
    temp_data = [0, 0, 0, 0]
    temp_data[3] = version & 0x00FF
    temp_data[2] = (version >> 8) & 0x00FF
    temp_data[1] = (version >> 16) & 0x00FF
    temp_data[0] = (version >> 24) & 0x00FF

    for i in [0, 1, 2, 3]:
      if temp_data[i] > 127:
        temp_data[i] = temp_data[i] - 256

    bin_size0 = struct.pack('b', temp_data[0])
    bin_size1 = struct.pack('b', temp_data[1])
    bin_size2 = struct.pack('b', temp_data[2])
    bin_size3 = struct.pack('b', temp_data[3])

    self.protofile.write(bin_size0)
    self.protofile.write(bin_size1)
    self.protofile.write(bin_size2)
    self.protofile.write(bin_size3)

    self.protofile.flush()

  # Write frame obj data into proto
  def writeFrameData_general(self, obj):
    if not isinstance(obj, self.proto):
      logging.fatal("[Attention] : writeFrameData_general() >> param shouble be given class.")
      return None
    proto_len = obj.ByteSize()
    temp_data = [0, 0, 0, 0]
    temp_data[3] = proto_len & 0x00FF
    temp_data[2] = (proto_len >> 8) & 0x00FF
    temp_data[1] = (proto_len >> 16) & 0x00FF
    temp_data[0] = (proto_len >> 24) & 0x00FF

    for i in [0, 1, 2, 3]:
      if temp_data[i] > 127:
        temp_data[i] = temp_data[i] - 256

    bin_size0 = struct.pack('b', temp_data[0])
    bin_size1 = struct.pack('b', temp_data[1])
    bin_size2 = struct.pack('b', temp_data[2])
    bin_size3 = struct.pack('b', temp_data[3])

    self.protofile.write(bin_size0)
    self.protofile.write(bin_size1)
    self.protofile.write(bin_size2)
    self.protofile.write(bin_size3)

    obj_bin = obj.SerializeToString()
    self.protofile.write(obj_bin)

    self.protofile.flush()

  # Write frame json data into proto
  def writeFrameData_json(self, json):
    obj = self.dict2pb(self.proto, simplejson.loads(json))
    self.writeFrameData_general(obj)

  # Convert dict to proto data
  def dict2pb(self, cls, adict):
    obj = cls()
    for field in obj.DESCRIPTOR.fields:
      if not field.label == field.LABEL_REQUIRED:
        continue
      if field.has_default_value:
        continue
      if not field.name in adict:
        raise ConvertException('Field "%s" missing from descriptor dictionary.' % field.name)
    for field in obj.DESCRIPTOR.fields:
      if not field.name in adict:
        continue
      msg_type = field.message_type
      if field.label == FD.LABEL_REPEATED:
        if field.type == FD.TYPE_MESSAGE:
          for sub_dict in adict[field.name]:
            item = getattr(obj, field.name).add()
            item.CopyFrom(self.dict2pb(msg_type._concrete_class, sub_dict))
        else:
          map(getattr(obj, field.name).append, adict[field.name])
      else:
        if field.type == FD.TYPE_MESSAGE:
          value = self.dict2pb(msg_type._concrete_class, adict[field.name])
          getattr(obj, field.name).CopyFrom(value)
        else:
          setattr(obj, field.name, adict[field.name])
    return obj

if __name__ == "__main__":
  pass