#include<iostream>

int normalize(int x) {
    if (x < 0) return 0;
    return x - 1;
}

int compute(int x, int y){
    int d = normalize(y);
    return x / d;
}

int main(){
    int x, y;
    std::cin >> x >> y;
    int result = compute(x, y);
    std::cout << result << std::endl;
    return 0;
}