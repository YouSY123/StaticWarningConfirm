#include<iostream>
#include<string.h>

#define BUFFER_SIZE 100

class Buffer{

private:
    char buff[BUFFER_SIZE];

public:
    char* write_buffer(int len, const char* dst){

        if(len > BUFFER_SIZE || len < 0){
            return nullptr;
        }

        int idx;
        for(idx = 0; idx < len; ++idx){
            buff[idx] = dst[idx];
        }
        buff[idx] = '\0';
    }
};


int main(){

    char input_str[BUFFER_SIZE];
    std::cin >> input_str;
    Buffer buffer;
    int len = strlen(input_str);

    if(len <= BUFFER_SIZE){
        buffer.write_buffer(len, input_str);
    }

    return 0;
}