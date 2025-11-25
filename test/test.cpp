#include<iostream>

int main(){
    int *test = new int[10];
    test[0] = 1;
    delete []test;
    test[0] = 1;
}