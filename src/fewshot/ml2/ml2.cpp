#include<string.h>
#include<stdlib.h>
#include<stdio.h>

char* func(int flag, const char* str, int len){

    char* p = nullptr;

    if(flag){
        p = (char*)malloc(len+1); 
        strncpy(p, str, len);
        p[len] = '\0';
    }
    else{
        p = (char*)malloc(5);
        strcpy(p, "None");
    }

    return p;
}


int main(){

    const char str[10] = "string";
    char* str_ptr = func(1, str, 6);
    printf("%s\n", str_ptr);
    free(str_ptr);

}