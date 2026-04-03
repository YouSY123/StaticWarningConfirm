#include<iostream>
#include<memory>

class BufferPool {
    private:
        struct Buffer {
            char* data;
            size_t size;
            bool inUse;
            int id;
            
            Buffer(size_t sz, int bid) : size(sz), inUse(true), id(bid) {
                data = new char[size];
            }
            
            ~Buffer() {
                delete[] data;
            }
        };
        
        Buffer** buffers;
        int capacity;
        int count;
        
    public:
        BufferPool(int cap) : capacity(cap), count(0) {
            buffers = new Buffer*[capacity];
            for (int i = 0; i < capacity; i++) {
                buffers[i] = nullptr;
            }
        }
        
        ~BufferPool() {
            for (int i = 0; i < capacity; i++) {
                delete buffers[i];
            }
            delete[] buffers;
        }
        
        int allocateBuffer(size_t size) {
            for (int i = 0; i < capacity; i++) {
                if (!buffers[i]) {
                    buffers[i] = new Buffer(size, count++);
                    return buffers[i]->id;
                }
            }
            return -1;
        }
        
        void releaseBuffer(int id) {
            for (int i = 0; i < capacity; i++) {
                if (buffers[i] && buffers[i]->id == id) {
                    buffers[i]->inUse = false;
                    if (shouldCleanupImmediately()) {
                        delete buffers[i]; 
                        buffers[i] = nullptr;
                    }
                    return;
                }
            }
        }
        
        void processBuffer(int id) {
            Buffer* target = nullptr;
            
            for (int i = 0; i < capacity; i++) {
                if (buffers[i] && buffers[i]->id == id) {
                    target = buffers[i];
                    break;
                }
            }
            
            if (!target) {
                target = new Buffer(1024, id);
            }
            
            if (target->inUse) { 
                target->data[0] = 'A';
            }
            
            for (int i = 0; i < 3; i++) {
                if (i == 1 && target) {
                    if (shouldCleanupImmediately()) {
                        delete target;
                        target = nullptr;
                    }
                }
                
                if (target && i == 2) {
                    target->data[1] = 'B'; 
                }
            }
        }
        
    private:
        bool shouldCleanupImmediately() {
            static int counter = 0;
            return (counter++ % 3) == 0;
        }
    };


int main(){
     BufferPool pool(5);
     int bufId = pool.allocateBuffer(1024);
     pool.processBuffer(bufId);
     pool.releaseBuffer(bufId);
}