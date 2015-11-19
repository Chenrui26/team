# reimplement project 1 in Python, and continue using python for the projects in future due to efficiency reason
import heapq

FILE_NAME = 'processes.txt'
FCFS = 'FCFS'
PWA = 'PWA'
SRT = 'SRT'
ID = 'ID'

CPU_IDLE = -1

STATUS_RUNNING = 0
STATUS_SUSPENDED = 1
STATUS_STOPPED = 2
STATUS_TERMINATED = 3

CONTEXT_SWITCH_PROCESS = 0
PROCESS_POOL = []

REPORT_FILE_NAME = "simout.txt"
#ONLY STORE INDEX IN ALL CONTAINERS
class ScProcess(object):
	"""docstring for ScProcess"""
	def __init__(self, file_pos, proc_num, burst_time, num_burst, io_time, priority):
		super(ScProcess, self).__init__()
		self.id = proc_num
		self.io_len = io_time
		self.priority = priority
		self.burst_len = burst_time
		self.burst_num = num_burst

		self.burst_num_r = num_burst
		self.burst_len_r = 0
		self.io_len_r = 0

		self.burst_len_total = 0
		self.pending_len_total = 0
		self.turnaround_len_total = 0
		self.queue_len_total = 0

		self.wait_len_current = 0

		self.status_io = STATUS_STOPPED
		self.status_burst = STATUS_STOPPED

		self._comparating_mode = PWA
		self._current_index = 0
	def __eq__(self, other):
		return self.id == other.id
	# start the burst when burst_len_r is 0, otherwise continues the previous burst
	def __str__(self):
		return 'Process ( %d ) (status = %d, %d) priority = %d _current_index = %d' % (self.id, self.status_burst, self.status_io, self.priority, self._current_index)
	def burst_start(self):
		if self.status_burst != STATUS_RUNNING:
			self.status_burst = STATUS_RUNNING
			if self.burst_len_r == 0 and self.burst_num_r == 0:
				raise Exception('burst start is called but the process is terminated' + str(self.id))
			if self.burst_len_r == 0:
				self.burst_num_r -= 1
				self.burst_len_r = self.burst_len
				return 'P%d started using the CPU' % self.id
			else:
				return 'P%d started using the CPU' % self.id
			self.wait_len_current = 0 # set the current waiting length to 0
		return ''

	# only when burst_len is 0, stop it, otherwise it's not finished an will give an error
	def burst_stop(self):
		if self.status_burst != STATUS_STOPPED:
			self.status_burst = STATUS_STOPPED
			if (self.burst_len_r != 0):
				raise Exception('burst stop is called but the current burst is not finished' + str(self.id))
			return 'P%d completed its CPU burst' % self.id
		else:
			return ''
	# keep burst data
	def burst_pending(self):
		if self.status_burst != STATUS_SUSPENDED:
			self.status_burst = STATUS_SUSPENDED
			return 'P%d suspended' % self.id
		else:
			return ''
	#terminate the process only if the process runs out its burst number and current burst
	def burst_terminate(self):
		if self.status_burst != STATUS_TERMINATED:
			self.status_burst = STATUS_TERMINATED
			self.status_io = STATUS_STOPPED
			if self.burst_len_r != 0 or self.burst_num_r != 0:
				raise Exception('burst terminate is called but the current burst is not finished' + str(self.id))
			return 'P%d terminated' % self.id
		else:
			return ''
	def io_start(self):
		if self.status_io != STATUS_RUNNING:
			self.status_io = STATUS_RUNNING
			self.io_len_r = self.io_len
			return 'P%d performing I/O' % self.id
		return ''
	def io_stop(self):
		if self.status_io != STATUS_STOPPED:
			self.status_io = STATUS_STOPPED
			return 'P%d completed I/O' % self.id
		return ''
	def io_pending(self):
		if self.status_io != STATUS_SUSPENDED:
			self.status_io = STATUS_SUSPENDED
			return 'P%d suspended using IO' % self.id
		return ''

	def __lt__(self, other):
		if (other is None):
			return False
		if (self._comparating_mode != other._comparating_mode):
			return False
		if (self._comparating_mode == ID):
			return self.id < other.id
		elif (self._comparating_mode == FCFS):
			return self._current_index < other._current_index
		elif (self._comparating_mode == PWA):
			return (self.priority < other.priority) or (self.priority == other.priority and self._current_index < other._current_index)
		elif (self._comparating_mode == SRT):
			return (self.burst_len < other.burst_len) or (self.burst_len == other.burst_len and self._current_index < other._current_index)
		return False

class ScProcessQueue(object):
	def __init__(self, mode = FCFS):
		self.queue = []
		self._index = 0
		self.mode = mode;
	def push(self, value):
		PROCESS_POOL[value]._comparating_mode = self.mode
		PROCESS_POOL[value]._current_index = self._index
		heapq.heappush(self.queue, (PROCESS_POOL[value], value))
		self._index += 1
	def pushlist(self, value):
		for i in value:
			self.push(i)
	def _push_raw(self, value):
		PROCESS_POOL[value]._comparating_mode = self.mode
		heapq.heappush(self.queue, (PROCESS_POOL[value], value))
	def pop(self):
		if (len(self.queue) == 0):
			return -1
		l = self.get_inorder()
		value = heapq.heappop(self.queue)
		if (value[1] != l[0][1]):
			print PROCESS_POOL[value[1]].id
			print PROCESS_POOL[l[0][1]].id
			raise Exception('WTF')
		return value[1]
	def size(self):
		return len(self.queue)
	def get_inorder(self):
		return heapq.nsmallest(len(self.queue), self.queue); # this use sort to create a new list
	def tostring(self):
		if (len(self.queue) == 0):
			r = '[Q]'
			return r
		r = '[Q'
		for i in self.get_inorder():
			r = r + ' %d' % PROCESS_POOL[i[1]].id
		r += ']'
		return r
	def contains(self, item):
		for i in self.queue:
			if i[1] == item:
				return True
		return False
	def remove(self, item):
		l = []
		while (True):
			item_ = self.pop();
			if item == item_:
				break
			l.append(item_)
		for i in l:
			self._push_raw(i)
	def update(self):
		heapq.heapify(self.queue)

class ScProcessPool(object):
	def __init__(self):
		self.pool = []
	def add(self, process):
		self.pool.insert(len(self.pool), process)
	def parse(self):
		f = open(FILE_NAME).readlines()
		count = 0
		for line in f:
			#parse the line:
			if line[0] == '#':
				continue
			l = line.split('|');
			l[len(l)-1] = l[len(l) - 1][:len(l[len(l) - 1])-1 ]
			#validate the line:
			if l[0] != '#' and len(l) == 5 :
				num_l = [0]*5
				count += 1
				for i in xrange(len(l)):
					try:
						num_l[i] = int(l[i])
					except ValueError:
						break
				self.add(ScProcess(count, num_l[0], num_l[1], num_l[2], num_l[3], num_l[4]));
	def __str__(self):
		string = 'ScProcessPool: '
		for p in self.pool:
			string += str(p)
		return string

class ScCPUEmulator(object):
	def __init__(self, t):
		self.type = t # type of queue
		self.processes = PROCESS_POOL
		self.q = ScProcessQueue(t) # queue of the specific type
		self.t = 0 # simulate time for the CPU
		self.CONTEXT_SWITCH_LEN = 13
		self.CONTEXT_SWITCH_PROCESS = 0 # context switch process is the super process.
		self.status = STATUS_STOPPED
		self.CONTEXT_PROCESS = ScProcess(-1, -1, self.CONTEXT_SWITCH_LEN, 1, 0, -1);
		PROCESS_POOL.insert(0, self.CONTEXT_PROCESS)
		self.q.pushlist(range(1, len(PROCESS_POOL)))
		self.burst_process = -1
		self.pending_process = -1

		self.context_switch_count = 0

	def terminate(self):
		self.status = STATUS_TERMINATED
		self.timestamp("Simulator for " + self.type + ' ended')
	def processes_terminated(self):
		# check if all processes is terminated
		for p in xrange(1,len(self.processes)):
			if PROCESS_POOL[p].status_burst != STATUS_TERMINATED:
				return False
		return True

	def update(self):
		# preempt
		finished = []
		timestamps = []
		priority_changed = []
		for p in xrange(len(PROCESS_POOL)):
			if p == self.pending_process:
				PROCESS_POOL[p].pending_len_total += 1

			if PROCESS_POOL[p].status_burst == STATUS_RUNNING:
				PROCESS_POOL[p].burst_len_total += 1
				PROCESS_POOL[p].burst_len_r -= 1
			if PROCESS_POOL[p].status_io == STATUS_RUNNING:
				PROCESS_POOL[p].io_len_r -= 1

			if self.q.contains(p):
				PROCESS_POOL[p].wait_len_current += 1
				PROCESS_POOL[p].queue_len_total += 1

			# if current type is PWA: increase the priority
			if self.type == PWA:
				if (PROCESS_POOL[p].wait_len_current > 3*PROCESS_POOL[p].burst_len):
					if (PROCESS_POOL[p].priority > 0):
						PROCESS_POOL[p].priority -= 1
					PROCESS_POOL[p].wait_len_current = 0

			# change status
			if PROCESS_POOL[p].burst_len_r == 0 and PROCESS_POOL[p].status_burst == STATUS_RUNNING:
				if PROCESS_POOL[p].burst_num_r == 0:
					result = PROCESS_POOL[p].burst_terminate()
					if result != '':
						self.timestamp(result)
				else:
					result = PROCESS_POOL[p].burst_stop()
					if result != '':
						r = PROCESS_POOL[p].io_start()
						self.timestamp(result)
						self.timestamp(r)

			if p != 0 and PROCESS_POOL[p].io_len_r == 0 and PROCESS_POOL[p].status_io == STATUS_RUNNING and PROCESS_POOL[p].status_burst != STATUS_TERMINATED:
				result = PROCESS_POOL[p].io_stop()
				if result != '':
					timestamps.append(result)
					finished.append(p)
		for i in finished:
			PROCESS_POOL[i].wait_len_current = 0
		# io completed:
		# everything finished is in finished: preempt with the things in finished
		queue_when_complete = self.q.tostring()
		self.q.pushlist(finished)
		result = self.preempt_check()
		if (len(result) != 0):
			for j in timestamps:
				self.timestamp(j, queue_when_complete)
			for i in result:
				self.timestamp(i)
		else:
			for i in timestamps:
				self.timestamp(i)
		self.q.update()

	def preempt_check(self):
		timestamps = []
		for item in self.q.queue:
			was_bursting = self.preempt(item[1])
			if (was_bursting != -1):
				timestamps.append('P%d preempted by P%d' %(PROCESS_POOL[was_bursting].id, PROCESS_POOL[item[1]].id))	
		return timestamps
	def preempt(self, item):
		# get preempt
		bursting = -1
		if item == self.burst_process:
			return bursting
		if self.type == SRT:
			if PROCESS_POOL[item].burst_len < PROCESS_POOL[self.burst_process].burst_len_r:
				bursting = self.replace_process(item)
		elif self.type == PWA:
			if PROCESS_POOL[item].priority < PROCESS_POOL[self.burst_process].priority:
				bursting = self.replace_process(item)
		return bursting

	def replace_process(self, item):
		bursting = self.burst_process
		if (bursting == -1 or bursting == 0):
			bursting = self.pending_process	
		if (PROCESS_POOL[bursting].status_burst == STATUS_TERMINATED):
			return -1
		self.push_process(item)
		#self.timestamp('P%d preempted by P%d' %(PROCESS_POOL[busting].id, PROCESS_POOL[item].id))
		return bursting

	def timestamp(self, string, queue = ''):
		if string[0:2] == 'P-': # mute the context switch process
			return
		if queue == '':
			print ("time %dms: " % self.t) + string + ' ' + self.q.tostring()
		else:
			print ("time %dms: " % self.t) + string + ' ' + queue

	def start(self):
		self.timestamp("Simulator started for " + self.type)

	def context_change(self):
		self.burst_process = self.CONTEXT_SWITCH_PROCESS;
		PROCESS_POOL[self.CONTEXT_SWITCH_PROCESS] = ScProcess(-1, -1, self.CONTEXT_SWITCH_LEN, 1, 0, -1)
		PROCESS_POOL[self.CONTEXT_SWITCH_PROCESS].burst_start()
		self.context_switch_count += 1

	def push_process(self, process = -1):
		r = ''
		if (self.burst_process == 0 and self.pending_process == 0):
			raise Exception("CONTEXT SWITCH SHOULDN'T BE IN PENDING PROCESS")
		if (process != -1): # force to replace the current bursting and pending process with the one in queue
			old = -1
			current_bursting = self.burst_process
			current_pending  = self.pending_process
			if (current_bursting != 0):
				old = current_bursting
			elif (current_pending != 0):
				old = current_pending
			if old != -1:
				PROCESS_POOL[old].burst_pending()
				self.q.push(old) # the old one should be pushed to exactly same position in the queue
				self.q.remove(process)
				self.pending_process = process
				self.context_change()

		if self.burst_process != -1 and (PROCESS_POOL[self.burst_process].status_burst == STATUS_STOPPED or PROCESS_POOL[self.burst_process].status_burst == STATUS_TERMINATED):
				self.burst_process = self.pending_process
				self.pending_process = -1
				if (self.burst_process != -1):
					r = PROCESS_POOL[self.burst_process].burst_start()
					if (r != ''):
						self.timestamp(r)

		if self.burst_process == -1 and self.q.size() > 0:
			self.pending_process = self.q.pop()
			self.context_change()
		return r
	def run(self):
		self.start()
		while not self.processes_terminated():

			self.push_process()
			self.t += 1
			self.update()

			# if self.t == 1551 or self.t == 1277:
			# 	print self.q.tostring()
			# 	for i in PROCESS_POOL:
			# 		print str(i)
		self.terminate()

	def report_statistic(self):
		total_b = 0.0
		total_w = 0.0
		total_t = 0.0
		count = 0
		for p in self.processes:
			if (p.id == -1):
				continue
			count += p.burst_num
			total_b += p.burst_len_total
			total_w += p.queue_len_total
			total_t += (p.queue_len_total + p.pending_len_total + p.burst_len_total)
		return 'Algorithm %s\n-- average CPU burst time: %.2f ms\n-- average wait time: %.2f ms\n-- average turnaround time: %.2f ms\n-- total number of context switches: %d' %(self.type, total_b/count, total_w/count, total_t/count, self.context_switch_count)

if __name__ == '__main__':
	pool = ScProcessPool()
	pool.parse()
	PROCESS_POOL = pool.pool[:]
	emulator = ScCPUEmulator(FCFS)
	emulator.run()
	print '\n'
	f = open(REPORT_FILE_NAME, 'a')
	f.write(emulator.report_statistic() + '\n')
	f.close()

	pool = ScProcessPool()
	pool.parse()
	PROCESS_POOL = pool.pool[:]
	emulator = ScCPUEmulator(SRT)
	emulator.run()
	print '\n'
	f = open(REPORT_FILE_NAME, 'a')
	f.write(emulator.report_statistic() + '\n')
	f.close()

	pool = ScProcessPool()
	pool.parse()
	PROCESS_POOL = pool.pool[:]
	emulator = ScCPUEmulator(PWA)
	emulator.run()
	print '\n'
	f = open(REPORT_FILE_NAME, 'a')
	f.write(emulator.report_statistic() + '\n')
	f.close()