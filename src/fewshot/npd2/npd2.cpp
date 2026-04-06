#include<iostream>

struct Node{
    int x;
};

struct Node* n[10];

void init(int cnt){
    for(int i = 0; i < 10; i++){
        n[i] = nullptr;
    }
    for(int i = 0; i < cnt; i++){
        n[i] = new Node;
        n[i]->x = i;
    }
}

void print_node(int idx, int flag){
    if(!flag) return;
    printf("%d\n", n[idx]->x);
}

int main(){
    init(5);
    int a = 0, b = 0;
    for(int i = 0; i < 5; i++){
        a += 1;
        b += 2;
        print_node(a, b);
    }
}