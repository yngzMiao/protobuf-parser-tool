project(general_pb2)

aux_source_directory(${PROJECT_SOURCE_DIR} PB_FILES)

add_library(${PROJECT_NAME} STATIC ${PB_FILES})

include_directories(${PROJECT_SOURCE_DIR}
    ${GOOGLE_PROTOBUF_DIR}/include
)

link_directories(${GOOGLE_PROTOBUF_DIR}/lib/)

target_link_libraries(${PROJECT_NAME}
    protobuf
)
