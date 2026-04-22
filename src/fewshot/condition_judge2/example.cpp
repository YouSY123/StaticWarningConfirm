#include<stdlib.h>

#define ABCDEFG 100
#ifdef ABCDEFG
#define XYZ
#endif

int foo(int arg1)
{

    #ifdef XYZ
    int var = arg1 - ABCDEFG;
    return var;
    #endif

    return ABCDEFG;
}

void get_ptr(int arg1, char* get_ptr)
{

    int var1 = foo(arg1);
    if(var1 > 0)
    {
        char* ptr = nullptr;
        ptr = (char*)malloc(var1);
        get_ptr = ptr;
    }
    else
    {
        return;
    }
}

int main()
{
    char* pointer = nullptr;
    get_ptr(20, pointer);
    pointer[0] = 'a';
    return 0;
}