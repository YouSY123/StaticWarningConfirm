#include<stdlib.h>

int* get_ptr(){
    return nullptr;
}

int foo(){

    int size = 0;
    int* p;

    if(size != 0){
        p=(int*)malloc(size*sizeof(int));
    }
    else{
        p=get_ptr();
    }

    return p[0];
}

int main(){
    foo();
}