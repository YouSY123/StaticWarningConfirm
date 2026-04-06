int* get_pointer(int* arr, int size){

    int* p;

    for(int i = 0; i < size; i++){
        if (arr[i] > 0) {
            p = &arr[i];
            break;
        }
    }

    if(size == 0){
        return nullptr;
    } else {
        return p;
    }

}

int main(){
    int arr[] = {-1, -2, -3, -4, -5};
    int* ptr = get_pointer(arr, 5);
    if(ptr != nullptr){
        *ptr = 10;
    }
    return 0;
}