#include <iostream>
#include "General_buf_read.h"
#include "General_buf_write.h"
#include "Person.pb.h" 

namespace PersonProto {
  class Person;
};

namespace GeneralBuf {
  template <typename T>
  class GeneralProtoWriter;
  typedef GeneralProtoWriter<PersonProto::Person> PersonProtoWriter;
  template <typename T>
  class GeneralProtoReader;
  typedef GeneralProtoReader<PersonProto::Person> PersonProtoReader;
};

int main(int argc, char const *argv[])
{
  GeneralBuf::PersonProtoWriter writer;
  std::string filename = "Person_test.proto";
  int64_t version = 20191001;
  writer.startWriter(filename, version);

  PersonProto::Person *person1 = new PersonProto::Person();
  person1->set_id(100000);
  person1->set_name("zhangsan");
  person1->set_age(20);

  person1->add_email("123456@qq.com");
  person1->add_email("234567@qq.com");
  PersonProto::PhoneNumber *phone1 = person1->add_phone();
  PersonProto::PhoneNumber *phone2 = person1->add_phone();
  phone1->set_number("987654");
  phone1->set_type(PersonProto::PhoneType::MOBILE);
  phone2->set_number("876543");
  phone2->set_type(PersonProto::PhoneType::HOME);

  PersonProto::Address *addr = person1->mutable_address();
  addr->set_country("china");
  addr->set_detail("beijing");

  writer.write(person1);
  writer.stopWriter();

  GeneralBuf::PersonProtoReader reader;
  reader.startReader(filename);

  std::cout << "version : " << reader.getVersion() << "\n";
  std::cout << "cnt : " << reader.getFrameCount() << "\n";
  reader.setFrameIndex(0);
  PersonProto::Person *person = new PersonProto::Person();
  reader.read(person);
  person->PrintDebugString();

  return 0;
}
