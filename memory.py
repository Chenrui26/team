mem_table = ['.']*256
FT = "FT"
NF = "NF"
BF = "BF"

# member function to print the memory bitmap
def print_mem(m_t):
    for x in xrange(8):
        mem_line = ''.join(mem_table[x*32 : (x+1)*32-1])
        print(mem_line)

def set_mem(m_t, p_id, start, p_size):
    for entry in xrange(start, start+p_size):
        m_t[entry] = p_id

# get a list of nodes that contains the information of free blocks in memory
# each node is a tuple whose first value is the start index and second value is the size 
def get_free_list(m_t):
    result = []
    i = 0
    while i < 256:
        if m_t[i] == '.':
            len = 0
            j = i
            while (j < 256 and m_t[j] == '.'):
                len += 1
                j += 1
            result.append((i, len))
            i = j
        i += 1
    return result
    
# return true if there are memory available, else return false and need memory defragmentation    
def allocate_mem(m_t, p_id, p_size, type):
    #list to store the information for each block of free memory
    free_list = get_free_list(m_t)
    if type == FT:
        for block in free_list:
            if (block[1] >= p_size):
                set_mem(m_t, p_id, block[0], p_size)
                return True
        return False
    elif type == NF:
        first_skipped = False
        for block in free_list:
            if block[1] >= p_size:
                if first_skipped == False:
                    first_skipped = True
                else:
                    set_mem(m_t, p_id, block[0], p_size)
                    return True
        return False
    elif type == BF:
        bf_index = 0
        diff = 256
        available = False
        for block in free_list:
            if block[1] >= p_size:
                available = True
                if ((block[1] - p_size) < diff):
                    bf_index = block[0]
                    diff = block[1] - p_size
        if (available == True):
            set_mem(m_t, p_id, bf_index, p_size)
            return True
        else:
            return False
    else:
        print("unknow algorithm")
        return False

# get the index of the end of first free memory block
def first_free_end_index(m_t):
    first_free = False
    for i in xrange(256):
        if first_free == False:
            if m_t[i] == '.':
                #print("first fre starts at %d" %i)
                first_free = True
        else:
            if m_t[i] != '.':    
                return i-1
    return 0
    
# get the index of the end of memory
def mem_end_index(m_t):
    result = 0
    for i in xrange(256):
        if m_t[i] != '.':
            result = i
    return result

#get the list containing the information for memory
def get_mem_list(m_t):
    mem_list = []
    current_char = '.'
    for i in xrange(256):
        if m_t[i] != current_char:
            current_char = m_t[i]
            j = i
            mem_len = 0;
            while(j < 256 and m_t[j] == current_char):
                j += 1
                mem_len += 1
            if current_char != '.':
                mem_list.append((current_char, mem_len))
            i = j+1
    if len(mem_list) == 0:
        mem_list.append(('.', 256))
    return mem_list
    
def reallocate(mem_list, m_t):
    for i in xrange(256):
        m_t[i] = '.'
    index = 0
    for proc in mem_list:
        set_mem(m_t, proc[0], index, proc[1])
        index += proc[1]
    
# return the unit of moved memory
def defragmentation(m_t):
    result = mem_end_index(m_t)-first_free_end_index(m_t)
    proc_mem_list = get_mem_list(m_t)
    m_t = reallocate(proc_mem_list, m_t)
    return result
    
if __name__ == '__main__':
    print_mem(mem_table)
    print("\n");
    print("\n");
    # test set+mem
    set_mem(mem_table, 'A', 0, 2)
    
    set_mem(mem_table, 'B', 12, 5)
    
    set_mem(mem_table, 'C', 22, 24)
    
    #allocate_mem(mem_table, 'D', 10, 'FT')
    
    print_mem(mem_table)
    
    freelist = get_free_list(mem_table) 
        
    allocate_mem(mem_table, 'T', 4, "NF")
    
    print("\n\n")
    print_mem(mem_table)
    
    print(first_free_end_index(mem_table))
    print(mem_end_index(mem_table))
    
    defragmentation(mem_table)
    print_mem(mem_table)
