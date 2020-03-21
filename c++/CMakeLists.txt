cmake_minimum_required(VERSION 3.0)
project(example_person)

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")

set(GOOGLE_PROTOBUF_DIR ${PROJECT_SOURCE_DIR}/protobuf)
set(PROTO_PB_DIR ${PROJECT_SOURCE_DIR}/proto_pb2)
set(PROTO_BUF_DIR ${PROJECT_SOURCE_DIR}/proto_buf)

add_subdirectory(proto_pb2)

include_directories(${PROJECT_SOURCE_DIR}
    ${PROTO_PB_DIR} ${PROTO_BUF_DIR}
)

add_executable(${PROJECT_NAME} example_person.cpp )

target_link_libraries(${PROJECT_NAME}
    general_pb2)

install(TARGETS ${PROJECT_NAME}
  RUNTIME DESTINATION ${PROJECT_SOURCE_DIR})
