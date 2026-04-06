#include <stdlib.h>

typedef struct Buf {
    char *data;
} Buf;

static Buf* create_buf(size_t n) {
    Buf *b = (Buf*)malloc(sizeof(Buf));
    if (!b) return NULL;

    b->data = (char*)malloc(n);
    if (!b->data) {
        free(b);
        return NULL;
    }
    return b;
}

int handle(int flag) {
    Buf *b = create_buf(128);
    if (!b) return -1;

    if (flag > 0) {
        b = create_buf(64);
        if (!b) return -2;
    }

    free(b->data);
    free(b);
    return 1;
}

int main(){
    handle(1);
    return 0;
}