class Node{
    
public:
    int* value;
    Node* next;

    Node(int val) {
        value = new int(val);
        next = nullptr;
    }

    ~Node() {
        delete value;
    }

};


void processList(Node* head, bool flag){

    Node* current = head;
    Node* toDelete = nullptr;

    while(current != nullptr){
        if(flag && current->value != nullptr){
            delete current->value;
            current->value = nullptr;

            toDelete = current;
        }
        current = current->next;

        if(toDelete != nullptr && flag){
            delete toDelete;
        }
    }

}

void createAndProcess(){
    Node* head = new Node(1);
    head->next = new Node(2);
    head->next->next = new Node(3);

    processList(head, true);
}

int main(){
    createAndProcess();
    return 0;
}