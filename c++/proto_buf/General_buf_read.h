#ifndef GENERAL_BUF_READ_H_
#define GENERAL_BUF_READ_H_

#include <fstream>
#include <string>
#include <vector>

namespace GeneralBuf {

template <typename T>
class GeneralProtoReader {
  typedef struct ProtoInfo {
    size_t prtPos;
    size_t prtLen;
  } ProtoInfo_t;

  public:
    int startReader(const std::string& filename);
    int read(T* t);
    uint32_t getVersion() const { return version; }
    int setFrameIndex(const int pos);
    int getFrameCount() const { return mProtoInfoVec.size(); };
    void stopReader();

  private:
    size_t GetFileSize(std::ifstream& ifs);
    std::string mFileName;
    std::ifstream mIfs;
    std::vector<char> mProtoBufVec;
    std::vector<ProtoInfo_t> mProtoInfoVec;
    uint32_t version;
    int mInput_cnt;
};

template <typename T>
int GeneralProtoReader<T>::startReader(const std::string& filename){
  mFileName = filename;
  mInput_cnt = 0;

  mIfs.open(mFileName.c_str(), std::ofstream::binary);
  if (!mIfs.is_open())
    return -1;
  
  size_t fileSize = GetFileSize(mIfs);
  size_t max_proto_len = 0;

  uint8_t tran_ver[4];
  mIfs.read((char *)tran_ver, 4);
  version = (tran_ver[0] << 24) & 0xFF000000;
  version |= (tran_ver[1] << 16) & 0x00FF0000;
  version |= (tran_ver[2] << 8) & 0x0000FF00;
  version |= (tran_ver[3]) & 0x000000FF;

  size_t cur_pos = 4;
  ProtoInfo_t protoInfo;

  while (cur_pos < fileSize) {
    size_t proto_len = 0;
    char temp_len[4];
    mIfs.read(temp_len, 4);
    proto_len = (temp_len[0] << 24) & 0xFF000000;
    proto_len |= (temp_len[1] << 16) & 0x00FF0000;
    proto_len |= (temp_len[2] << 8) & 0x0000FF00;
    proto_len |= (temp_len[3]) & 0x000000FF;
    mIfs.seekg(proto_len, mIfs.cur);

    protoInfo.prtLen = proto_len;
    protoInfo.prtPos = cur_pos + 4;

    mProtoInfoVec.push_back(protoInfo);
    cur_pos += 4 + proto_len;
    if (proto_len > max_proto_len)
      max_proto_len = proto_len;
  }

  if (mProtoBufVec.capacity() < max_proto_len)
    mProtoBufVec.reserve(max_proto_len);

  return 0;
}

template <typename T>
size_t GeneralProtoReader<T>::GetFileSize(std::ifstream& ifs) {
  size_t cur_pos = ifs.tellg();
  ifs.seekg(0, ifs.end);
  size_t size = ifs.tellg();
  ifs.seekg(cur_pos);
  return size;
}

template <typename T>
int GeneralProtoReader<T>::read(T* t) {
  if (mInput_cnt < 0 || mInput_cnt >= mProtoInfoVec.size())
    return -1;

  ProtoInfo_t &frame_info = mProtoInfoVec[mInput_cnt];
  mIfs.seekg((int)frame_info.prtPos);
  mIfs.read(&mProtoBufVec[0], frame_info.prtLen);
  
  if (t->ParseFromArray((uint8_t *)(&mProtoBufVec[0]), frame_info.prtLen))
    return 0;
  
  return -1;
}

template <typename T>
int GeneralProtoReader<T>::setFrameIndex(const int pos) {
  mInput_cnt = pos;
  return 0;
}

template <typename T>
void GeneralProtoReader<T>::stopReader() {
  mProtoInfoVec.clear();
  mProtoBufVec.clear();

  if (mIfs.is_open())
    mIfs.close();
}
}

#endif