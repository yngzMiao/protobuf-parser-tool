# -*- coding:UTF-8 -*-

import sys
import os
import proto_pb2.Person_pb2 as GeneralProto
import proto_buf.Person_buf_read as PersonRead
import proto_buf.Person_buf_write as PersonWrite
import simplejson


if __name__ == "__main__":
  if not os.path.exists(os.path.join(os.getcwd(), "data")):
    os.mkdir("data")
  
  protofile = os.path.join(os.getcwd(), "data/Person_test.proto")
  version = 20191001
  writer = PersonWrite.GeneralProtoWriter(protofile, GeneralProto.Person, version)

  person1 = GeneralProto.Person()
  person1.id = 100000
  person1.name = "zhangsan"
  person1.age = 20

  person1.email.append("123456@qq.com")
  person1.email.append("234567@qq.com")
  phone1 = person1.phone.add()
  phone2 = person1.phone.add()
  phone1.number = "987654"
  phone1.type = GeneralProto.PhoneType.MOBILE
  phone2.number = "876543"
  phone2.type = GeneralProto.PhoneType.HOME

  addr = person1.address
  addr.country = "china"
  addr.detail = "beijing"

  writer.writeFrameData_general(person1)

  person2 = '{"name":"lisi","age":22,"id":200000,"email":["345678@qq.com","456789@qq.com"],"phone":[{"type":1,"number":"765432"},{"type":2,"number":"654321"}],"address":{"country":"china","detail":"nanjing"}}'

  writer.writeFrameData_json(person2)
  writer.stopWriter()

  reader = PersonRead.GeneralProtoReader(protofile, GeneralProto.Person)
  version_read = reader.getVersion()

  reader.setFrameIndex(0)
  print(reader.getFrameData_general("id"))
  print(reader.getFrameData_general("name"))
  print(reader.getFrameData_general("age"))
  print(reader.getFrameData_general("email"))
  print(reader.getFrameData_general("phone"))
  print(reader.getFrameData_general("address.country"))
  print(reader.getFrameData_general("address.detail"))
  
  reader.setFrameIndex(1)
  json = reader.getFrameData_json()
  print(json)


