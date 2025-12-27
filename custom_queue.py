class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.pop(0)
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)
    
    def peek(self):
        if self.is_empty():
            return None
        return self.items[0]


class PriorityQueue(Queue):
    def __init__(self):
        super().__init__()
        self.is_priority = False
    
    def check_priority(self):
        if self.size() >= 10 and not self.is_priority:
            self.is_priority = True
            return True
        elif self.size() <= 5 and self.is_priority:
            self.is_priority = False
            return False
        return self.is_priority