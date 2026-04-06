#include<stdio.h>

int *buff;
int buff_len;

void alloc_buff(int size){
    buff = new int[size];
    buff_len = size;
}

void write_buff(int idx, int val){
    if(idx < buff_len){
        buff[idx] = val;
    }
}

int main(){
    int s, i, v;
    scanf("%d", &s);
    alloc_buff(s);
    scanf("%d %d", &i, &v);
    write_buff(i, v);
    return 0;
}