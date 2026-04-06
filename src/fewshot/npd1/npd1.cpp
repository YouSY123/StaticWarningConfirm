#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node *next;
} Node;

static Node* maybe_get(int flag) {
    if (flag > 0) {
        Node *n = (Node*)malloc(sizeof(Node));
        if (!n) return NULL;
        n->value = 42;
        n->next = NULL;
        return n;
    }
    return NULL;
}

int foo(int a, int b) {
    Node *p = maybe_get(a);
    if (b < 0) {
        return -1;
    }
    else{
        return p->value + b;
    }
}

int main(){
    int result = foo(-1, 5);
    printf("Result: %d\n", result);
    return 0;
}