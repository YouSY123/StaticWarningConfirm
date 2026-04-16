#include<stdlib.h>
#include<stdio.h>

int* func1(int num)
{
    int* ret_p = nullptr;

    if(num <= 0)
    {
        return ret_p;
    }
    else
    {
        ret_p = (int*)malloc(num*sizeof(int));
        for(int i = 1; i <= num; ++i)
        {
            ret_p[i] = i;
        }
        return ret_p;
    }
}

void func2(int flag, int num)
{
    if(!flag)
    {
        return;
    }
    else
    {
        int* ptr = func1(num);
        int* ptr2 = ptr;
        for(int i = 1; i <= num; i++)
        {
            printf("%d\n", ptr[i]);
        }
        free(ptr);
    }
}

int main()
{
    int value1 = (1 + 2) / 2;
    func2(1, value1); 

    int value2 = value1 - 2;
    func2(0, value2);
}