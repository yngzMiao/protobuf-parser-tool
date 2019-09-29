## 依赖
```
pip install protobuf
pip install simplejson
```
注意：安装过程中，可能存在权限问题，直接`sudo`就可以了

## 使用
1. 创建`.proto`文件，规定`proto`文件格式。`prebuild`文件夹下，生成对应的`pb`文件:
```
bash make.sh
```
注意：需要修改`make.sh`的内容，指定`proto`文件

2. 依照`example_person.py`进行`proto`文件写入和解析。
```
python example_person.py
```

protobuf是Google开源的一个跨平台的结构化数据存储格式。可用于通讯协议、数据存储等领域的语言无关、平台无关、可扩展的序列化结构数据格式。

## 前言
说起proto的用法，可能最熟悉的莫过于以下两句：
```python
obj.ParseFromString(data)
data = obj.SerializeToString()
```
其中，obj是proto中message的实例对象，data是序列化之后的二进制数据。

**ParseFromString()将二进制数据反序列化，最终保存在obj中；SerializeToString()则将obj进行序列化，赋值给data**。

这部分网络上的资料很多，但是如何将这些数据在文件中保存起来，却很少有涉及。

本文就这部分进行讲解，其中代码部分已经开源，有需求的可以到以下链接获取：

**码云**：[https://gitee.com/yngzMiao/protobuf-parser-tool](https://gitee.com/yngzMiao/protobuf-parser-tool)

**GitHub**：[https://github.com/yngzMiao/protobuf-parser-tool](https://github.com/yngzMiao/protobuf-parser-tool)

## 如何保存
将序列化后的二进制数据保存成文件，很简单：
```python
fw = open("xxx.proto", "wb")
fw.write(...)
fw.close()
```
但是，如果单纯这样写进去，如何读取呢？如何才能获取一块完整的序列化的二进制数据呢？

本文采用记录二进制数据大小的方式，即：

**在每段序列化的二进制数据前，都放置4个字节大小的内容，这块内容用来保存接下来的二进制数据的字节长度**。

字节长度通过以下方法获得：
```python
proto_len = obj.ByteSize()
```
这块内容写入proto的方式：
```python
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
```
读取这块内容的方式：
```python
binval = [int(struct.unpack('b', temp_len[0])[0]),
          int(struct.unpack('b', temp_len[1])[0]),
          int(struct.unpack('b', temp_len[2])[0]),
          int(struct.unpack('b', temp_len[3])[0])]
          
re = (binval[0] << 24) & 0xFF000000
re = ((binval[1] << 16) & 0x00FF0000) | re
re = ((binval[2] << 8) & 0x0000FF00) | re
re = ((binval[3]) & 0x000000FF) | re
```
除此之外，我还添加了`版本`的内容。所谓版本，就是在proto的最开始的4字节，设置这个内容的本意在于：

由于proto更新频率快，添加字段或者删除字段可能也是常有的事，最好需要对每个生成的二进制文件进行标注，标明是按哪个版本的proto文件生成的。

## 接口说明
本文的常用的接口基本包含在`example_person.py`中，就对该文件进行讲解：
```python
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
  # 生成writer，需要指定三个参数：
  # 生成的二进制文件的路径，proto结构中的基本message，版本号(可忽略，默认值20191001)
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
  
  # 将obj对象直接写入到二进制文件中
  writer.writeFrameData_general(person1)

  person2 = '{"name":"lisi","age":22,"id":200000,"email":["345678@qq.com","456789@qq.com"],"phone":[{"type":1,"number":"765432"},{"type":2,"number":"654321"}],"address":{"country":"china","detail":"nanjing"}}'

  # 将json字符串写入到二进制文件中
  writer.writeFrameData_json(person2)
  # 关闭writer
  writer.stopWriter()

  # 生成reader，需要指定两个参数：
  # 需要解析的二进制文件的路径，proto结构中的基本message
  reader = PersonRead.GeneralProtoReader(protofile, GeneralProto.Person)
  # 获得版本号
  version_read = reader.getVersion()
  # 获得二进制数据的个数(帧数)
  frame_count = reader.getFrameCount()
  
  # 定位帧数(必须)
  reader.setFrameIndex(0)
  # 获得该帧的字段内容
  print(reader.getFrameData_general("id"))
  print(reader.getFrameData_general("name"))
  print(reader.getFrameData_general("age"))
  print(reader.getFrameData_general("email"))
  print(reader.getFrameData_general("phone"))
  print(reader.getFrameData_general("address.country"))
  print(reader.getFrameData_general("address.detail"))
  
  reader.setFrameIndex(1)
  # 将某帧的二进制内容解析，并转换成json字符串
  json = reader.getFrameData_json()
  print(json)
 ```

## 后言
如果喜欢本篇内容，就到`码云`或者`GitHub`点赞，谢谢。

如果有什么BUG或者反馈，欢迎提出。