## 介绍

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