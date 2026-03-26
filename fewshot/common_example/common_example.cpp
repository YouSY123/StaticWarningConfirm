#include<iostream>
#include<string.h>

void test(char* p){
    if(strcmp(p, "correct") == 0){
        std::cout << "correct" << std::endl;
        return;
    }
    delete[] p;
    return;
}

int main(){
    
    char* a = new char[10];
    char* b = new char[10];
    std::cin >> a;
    strcpy(b, "correct");

    test(a);
    test(b);

    delete[] a;
    delete[] b;
}