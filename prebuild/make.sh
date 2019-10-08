#! /bin/bash
./protoc -I=./ --python_out=./ Person.proto
./protoc -I=./ --cpp_out=./ Person.proto
