#/bin/bash

rm -r build
mkdir build && cd build 

cmake ..

make && make install

cd ..

./example_person
