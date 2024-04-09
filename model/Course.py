class Course():
    def __init__(self, courseName, hoursRequired, daySparsity="sparse", daySparsityWeight=2, hourSparsity="dense", hourSparsityWeight=1) -> None:
        '''
        sparsity: One of "sparse" or "dense".
        '''
        self.name = courseName
        self.hoursRequired = hoursRequired
        self.daySparsity = daySparsity
        self.daySparsityWeight = daySparsityWeight
        self.hourSparsity = hourSparsity
        self.hourSparsityWeight = hourSparsityWeight
    
    def __eq__(self, other):
        return self.name == other.name

    