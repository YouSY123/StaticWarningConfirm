#include<iostream>

void foo(char* p, int flag){
    printf("%s\n", p);
    if(flag == 1){
        delete[] p;
    }
}

int main(){
    char* str = new char[10];
    for(int i = 0; i < 3; i++){
        foo(str, i);
    }
    return 0;
}