#ifndef GENERAL_BUF_WRITE_H_
#define GENERAL_BUF_WRITE_H_

#include <fstream>
#include <string>

namespace GeneralBuf {
#define VERSION 20191001

template <typename T>
class GeneralProtoWriter {
  public:
    int startWriter(const std::string &filename, const int64_t version = VERSION);
    int write(T* t);
    void stopWriter();
  private:
    std::string mFileName;
    std::ofstream mOfs;
};

template <typename T>
int GeneralProtoWriter<T>::startWriter(const std::string &filename, const int64_t version) {
  mFileName = filename;
  mOfs.open(mFileName.c_str(), std::ofstream::binary);
  
  if (mOfs.is_open()) {
    unsigned char tran_ver[4];
    tran_ver[0] = version >> 24 & 0x00FF;
    tran_ver[1] = version >> 16 & 0x00FF;
    tran_ver[2] = version >> 8 & 0x00FF;
    tran_ver[3] = version >> 0 & 0x00FF;
    mOfs.write((char *)tran_ver, 4);
    return 0;
  }
  return -1;
}

template <typename T>
int GeneralProtoWriter<T>::write(T* t) {
  if(!mOfs.is_open() || t == nullptr)
    return -1;
  
  int byte_len = t->ByteSize();
  char temp_len[4];
  temp_len[3] = byte_len & 0x00FF;
  temp_len[2] = (byte_len >> 8) & 0x00FF;
  temp_len[1] = (byte_len >> 16) & 0x00FF;
  temp_len[0] = (byte_len >> 24) & 0x00FF;
  mOfs.write(temp_len, 4);
  if (!mOfs.good())
    return -1;

  if (byte_len > 0 && t->SerializeToOstream(&mOfs) == true)
    return 0;
  else
    return -1;
}

template <typename T>
void GeneralProtoWriter<T>::stopWriter() {
  if (mOfs.is_open())
    mOfs.close();
}
}

#endif