#! /usr/bin/env python

import random
from optparse import OptionParser
import collections

# process states
STATE_RUNNING = 'RUNNING'
STATE_READY = 'READY'
STATE_DONE = 'DONE'

# members of process structure
PROC_CODE = 'code_'
PROC_PC = 'pc_'
PROC_ID = 'pid_'
PROC_STATE = 'proc_state_'

# things a process can do
DO_COMPUTE = 'cpu'
DO_YIELD = 'yld'


class Scheduler:
    curr_proc: int
    ready: collections.deque
    done: list

    def __init__(self):
        # keep set of instructions for each of the processes
        self.proc_info = {}
        self.ready = collections.deque()
        self.curr_proc = -1
        self.done = []
        return

    def new_process(self):
        proc_id = len(self.proc_info)
        self.proc_info[proc_id] = {}
        self.proc_info[proc_id][PROC_PC] = 0
        self.proc_info[proc_id][PROC_ID] = proc_id
        self.proc_info[proc_id][PROC_CODE] = []
        self.proc_info[proc_id][PROC_STATE] = STATE_READY
        self.ready.append(proc_id)
        return proc_id

    def load(self, program_description):
        proc_id = self.new_process()
        tmp = program_description.split(':')
        if len(tmp) != 2:
            print('Bad description (%s): Must be number <x:y>')
            print('  where X is the number of instructions')
            print('  and Y is the percent change that an instruction is CPU not YIELD')
            exit(1)

        num_instructions, chance_cpu = int(tmp[0]), float(tmp[1]) / 100.0
        for i in range(num_instructions):
            if random.random() < chance_cpu:
                self.proc_info[proc_id][PROC_CODE].append(DO_COMPUTE)
            else:
                self.proc_info[proc_id][PROC_CODE].append(DO_YIELD)
        return

    # choose next proc using FIFO/FCFS scheduling, If pid==-1, then pid=self.curr_proc
    def next_proc(self, pid=-1):
        if pid == -1:
            pid = self.curr_proc
        pid += 1
        if pid >= self.get_num_active():
            pass

    def get_num_processes(self):
        return len(self.proc_info)

    def get_num_instructions(self, pid):
        return len(self.proc_info[pid][PROC_CODE])

    def get_instruction(self, pid, index):
        return self.proc_info[pid][PROC_CODE][index]

    def get_num_active(self):
        num_active = len(self.ready)
        return num_active

    def get_num_runnable(self):
        num_runnable = len(self.ready) + int(self.proc_info[self.curr_proc][PROC_STATE] == STATE_RUNNING)
        return num_runnable

    @staticmethod
    def space(num_columns):
        for i in range(num_columns):
            print('%10s' % ' ')

    def run(self):
        clock_tick1 = 0

        if len(self.proc_info) == 0:
            return

        # make first one active
        self.start_next_process()

        # OUTPUT: headers for each column
        print('%s' % 'Time', end='')
        for pid in range(len(self.proc_info)):
            print('%10s' % ('PID:%3d' % pid), end='')

        print('')

        # init statistics
        cpu_busy = 0

        while self.get_num_active() > 0:
            if self.curr_proc == -1:
                self.start_next_process()

            clock_tick1 += 1

            # if current proc is RUNNING and has an instruction, execute it
            # statistics clock_tick
            instruction_to_execute = ''
            if self.proc_info[self.curr_proc][PROC_STATE] == STATE_RUNNING and \
                    len(self.proc_info[self.curr_proc][PROC_CODE]) > 0:
                instruction_to_execute = self.proc_info[self.curr_proc][PROC_CODE].pop()

            # OUTPUT: print what everyone is up to
            print('%3d ' % clock_tick1, end='')
            for pid in range(len(self.proc_info)):
                if pid == self.curr_proc and instruction_to_execute != '':
                    print('%10s' % ('RUN:' + instruction_to_execute), end='')
                else:
                    print('%10s' % (self.proc_info[pid][PROC_STATE]), end='')

            print('')

            # If the current process has finished all instructions, change its state to done.
            if len(self.proc_info[self.curr_proc][PROC_CODE]) == 0:
                self.done.append(self.curr_proc)
                self.curr_proc = -1
                continue

            # if instruction_to_execute is an YIELD instruction, switch to ready state
            # and add an io completion in the future
            if instruction_to_execute == DO_YIELD:
                self.append_current_process()

        return clock_tick1

    def start_next_process(self):
        if len(self.ready) == 0:
            return False

        self.curr_proc = self.ready.popleft()
        self.proc_info[self.curr_proc][PROC_STATE] = STATE_RUNNING
        return True

    def append_current_process(self):
        self.proc_info[self.curr_proc][PROC_STATE] = STATE_READY
        self.ready.append(self.curr_proc)
        self.curr_proc = -1


#
# PARSE ARGUMENTS
#

parser = OptionParser()
parser.add_option('-s', '--seed', default=0, help='the random seed', action='store', type='int', dest='seed')
parser.add_option('-l', '--processlist', default='',
                  help='a comma-separated list of processes to run, in the form X1:Y1,X2:Y2,... where X is the number of instructions that process should run, and Y the chances (from 0 to 100) that an instruction will use the CPU or issue an YIELD',
                  action='store', type='string', dest='process_list')
parser.add_option('-p', '--printstats',
                  help='print statistics at end; only useful with -c flag (otherwise stats are not printed)',
                  action='store_true', default=False, dest='print_stats')
(options, args) = parser.parse_args()

random.seed(options.seed)

s = Scheduler()

# example process description (10:100,10:100)
for p in options.process_list.split(','):
    s.load(p)

print('Produce a trace of what would happen when you run these processes:')
for pid1 in range(s.get_num_processes()):
    print('Process %d' % pid1)
    for inst in range(s.get_num_instructions(pid1)):
        print('  %s' % s.get_instruction(pid1, inst))
    print('')
print('Important behaviors:')
print('  System will switch when the current process is FINISHED or ISSUES AN YIELD\n')

clock_tick = s.run()

if options.print_stats:
    print('')
    print('Stats: Total Time %d' % clock_tick)
    print('')
