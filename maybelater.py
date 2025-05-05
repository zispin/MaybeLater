import time
import random
import re
from collections import defaultdict
from heapq import heappush, heappop
import sys

class TimeMachine: #this lets me set and retrieve variables with timestaps
    def __init__(self):
        self.time_variables = defaultdict(list) #stores the timestamped variables
        
    def set_past_value(self, name, value, seconds_ago):
        #store the value with a timestamp in the past
        effective_time = time.time() - seconds_ago
        self.time_variables[name].append((effective_time, value))
        self.time_variables[name].sort(reverse=True)
        
    def get_past_value(self, name, current_value):
        #get the most recent value that is still in the past
        for time_set, val in self.time_variables.get(name, []):
            if time_set < time.time():
                return val
        return current_value
#this class is supposed to simulate quantum variables, but it doesn't work very well
class QuantumVariables:
    def __init__(self):
        self.maybe_values = {} #stores the maybe variables
        self.paradox_values = {} #stores the paradox variables that exists only after some time
        
    def get_value(self, name):
        if name in self.paradox_values:
            #check if the paradox has resolved
            if time.time() > self.paradox_values[name]['exists_after'] or random.random() < 0.3:
                return self.paradox_values[name]['value']
            raise ValueError("paradox not done!")
        if name in self.maybe_values:
            #maybe the value will exist
            if random.random() < 0.5:
                return self.maybe_values[name]
            raise ValueError("maybe variable doesn't exist")
        return None
#main interpreter class
class MaybeLaterInterpreter:
    def __init__(self):
        self.sequence_counter = 0
        self.event_queue = [] #normal evens
        self.procrastination_queue = [] #deferred events
        self.variables = {} #varaibles
        self.last_used = {} #track the use time for expiration
        self.quantum_vars = QuantumVariables()
        self.time_machine = TimeMachine()
        self.deadline = None
        self.panic_mode = False
        self.start_time = time.time()

    def load_program(self, ast):
        #load and catorize the program
        for node in ast:
            if node['type'] == 'deadline':
                self.deadline = time.time() + node['seconds']
            elif node['type'] == 'procrastinate_block':
                self.procrastination_queue.extend(node['block'])
            else:
                self.schedule_node(node)
                
    def run_program(self):
        #runa ll normal events
        while self.event_queue:
            self.process_events('normal')
            self.check_deadline()
            self.cleanup_expired_vars()
        #if the task is still procastinated, run it in panic mode
        if self.procrastination_queue:
            self.process_procrastination()
            time.sleep(1)
            print("\nfinally getting to procrastination tasks\n")
            
            while self.event_queue:
                self.process_events('procrastinate')
                self.check_deadline()
                self.cleanup_expired_vars()

    def schedule_node(self, node):
        #interepret each node type and schedule it
        if node['type'] == 'eventually_loop':
            for i in range(node['start'], node['end'] + 1):
                self.schedule_event({
                    'type': 'loop_iteration',
                    'var': node['var'],
                    'value': i,
                    'block': node['block']
                }, delay=0, priority=1)
        elif node['type'] == 'someday_cond':
            if random.random() < 0.7 or self.panic_mode:
                self.schedule_event(node, delay=0.1)
        elif node['type'] in ['meh_var', 'maybe_var', 'paradox_var', 'yesterdaze_var']:
            self.schedule_event(node, delay=0)
        elif node['type'] == 'print_stmt':
            self.schedule_event(node, delay=0)
        elif node['type'] == 'procrastinate_block':
            for stmt in node['block']:
                self.schedule_event(stmt, delay=0, priority=100)

    def schedule_event(self, event, delay=0, priority=0):
        #push the event into the event queue
        exec_time = time.time() + delay
        heappush(self.event_queue, (exec_time, priority, self.sequence_counter, event))
        self.sequence_counter += 1

    def process_events(self, phase):
        #execute teh events from the queue 
        while self.event_queue:
            exec_time, priority, seq, event = self.event_queue[0]
            if phase == 'procrastinate' and exec_time > time.time():
                if random.random() < 0.2:
                    time.sleep(random.uniform(0.1, 0.5)) #this will slow down the procrastination tasks
                break
            event = heappop(self.event_queue)[3]
            if phase == 'procrastinate':
                time.sleep(random.uniform(0.1, 0.3)) #delay for procrastination tasks
            self.execute_event(event, phase)

    def execute_event(self, event, phase):
        #execute one event based on its type
        if event['type'] == 'meh_var':
            self.variables[event['name']] = event['value']
            self.last_used[event['name']] = time.time()
        elif event['type'] == 'maybe_var':
            if random.random() < 0.5:
                self.quantum_vars.maybe_values[event['name']] = event['value']
        elif event['type'] == 'paradox_var':
            self.quantum_vars.paradox_values[event['name']] = {
                'value': event['value'],
                'exists_after': time.time() + random.randint(1, 3)
            }
        elif event['type'] == 'yesterdaze_var':
            self.time_machine.set_past_value(
                event['name'], 
                event['value'], 
                event['seconds_ago']
            )
        elif event['type'] == 'loop_iteration':
            current_value = event['value']
            var_name = event['var']
            self.variables[var_name] = current_value
            for stmt in event['block']:
                if stmt['type'] == 'someday_cond':
                    safe_globals = {'__builtins__': None}
                    safe_locals = {var_name: current_value}
                    try:
                        if eval(stmt['condition'], safe_globals, safe_locals):
                            for action in stmt['block']:
                                self.execute_event(action, phase)
                    except:
                        pass
                else:
                    self.execute_event(stmt, phase)
        elif event['type'] == 'someday_cond':
            try:
                current_i = self.variables.get('i', 1)
                if eval(event['condition'], {}, {'i': current_i}) or (self.panic_mode and random.random() < 0.8):
                    for stmt in event['block']:
                        self.schedule_event(stmt, delay=0.001 if self.panic_mode else 0.1)
            except:
                pass
        elif event['type'] == 'print_stmt':
            try:
                if event['expr'].startswith(('"', "'")):
                    print(event['expr'][1:-1])
                elif event['expr'] in self.variables:
                    print(self.variables[event['expr']])
                else:
                    result = eval(event['expr'], {'__builtins__': None}, self.variables)
                    print(result)
            except:
                pass

    def process_procrastination(self):
        #handle the task under time pressure
        print("\nbeginning procrastination tasks\n")
        start_time = time.time()
        timeout = 10 #max time to handle the task
        
        while self.procrastination_queue and time.time() - start_time < timeout:
            event = self.procrastination_queue.pop(0)
            delay = random.uniform(0.1, 1.0) * (1 + len(self.procrastination_queue)/10)
            if event['type'] == 'eventually_loop':
                for i in range(event['start'], event['end'] + 1):
                    self.schedule_event({
                        'type': 'loop_iteration',
                        'var': event['var'],
                        'value': i,
                        'block': event['block']
                    }, delay=delay + i * 0.1, priority=100)
            else:
                self.schedule_event(event, delay=delay, priority=100)
            if random.random() < 0.3:
                extra_delay = random.uniform(0.5, 1.5)
                print(f"got distracted for {extra_delay:.1f}s...")
                time.sleep(extra_delay)

        if self.procrastination_queue:
            print("time ran out for procrastination tasks")

    def get_all_variables(self):
        #return a dict of all the variables
        vars_copy = dict(self.variables)
        vars_copy.update(self.quantum_vars.maybe_values)
        for name in self.quantum_vars.paradox_values:
            try: vars_copy[name] = self.quantum_vars.get_value(name)
            except: pass
        for name in vars_copy:
            vars_copy[name] = self.time_machine.get_past_value(name, vars_copy[name])
        return vars_copy

    def check_deadline(self):
        #if the deadline is near twitch to panic mode
        if self.deadline and time.time() > self.deadline - 5:
            self.panic_mode = True
            new_queue = []
            seq = self.sequence_counter
            for t, p, s, e in self.event_queue:
                heappush(new_queue, (time.time() + 0.001, p, seq, e))
                seq += 1
            self.event_queue = new_queue
            self.sequence_counter = seq

    def cleanup_expired_vars(self):
        #remove the variables that are expired or not unused for a while unless we're in panic mode
        now = time.time()
        expired = [k for k, t in self.last_used.items() 
                  if now - t > 30 and not self.panic_mode]
        for var in expired:
            del self.variables[var]
            del self.last_used[var]
            
#parse the language and convert it to an AST
def parse_code(code):
    ast = []
    lines = [l.strip() for l in code.split('\n') if l.strip()]
    i = 0
    
    while i < len(lines):
        line = lines[i]
        if var_match := re.match(r'(meh|maybe|paradox|yesterdaze)\s+(\w+)\s*=\s*(.+?)(?:\s+ago\s+(\d+)s)?;', line): #ai helped me with this regex
            var_type, name, value, ago = var_match.groups()
            node = {'type': f'{var_type}_var', 'name': name, 'value': eval(value)}
            if var_type == 'yesterdaze': node['seconds_ago'] = int(ago)
            ast.append(node)
            i += 1
        elif line.startswith('eventually'):
            if match := re.match(r'eventually (\w+) from (\d+) to (\d+)\s*\{', line): #ai helped me with this regex
                var, start, end = match.groups()
                block, new_i = parse_code_block(lines, i)
                ast.append({'type': 'eventually_loop', 'var': var, 'start': int(start), 'end': int(end), 'block': block})
                i = new_i
        elif line.startswith('someday'):
            cond = re.match(r'someday \((.*)\)\s*\{', line).group(1) #this too
            block, new_i = parse_code_block(lines, i)
            ast.append({'type': 'someday_cond', 'condition': cond, 'block': block})
            i = new_i
        elif line.startswith('PRINT('):
            expr = re.match(r'PRINT\((.+)\);?', line).group(1) #and this
            ast.append({'type': 'print_stmt', 'expr': expr})
        elif line.startswith('deadline in'):
            secs = int(re.search(r'\d+', line).group())
            ast.append({'type': 'deadline', 'seconds': secs})
        elif line.startswith('procrastinate'):
            block, new_i = parse_code_block(lines, i)
            ast.append({'type': 'procrastinate_block', 'block': block})
            i = new_i
        else: i += 1
    return ast

def parse_code_block(lines, start_idx):
    block = []
    depth = 1
    i = start_idx + 1
    while i < len(lines) and depth > 0:
        line = lines[i].strip()
        depth += line.count('{') - line.count('}')
        if depth > 0 and line: block.append(line)
        i += 1
    return parse_code('\n'.join(block)), i

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python maybelater.py <filename.mlater>")
        sys.exit(1)
    interpreter = MaybeLaterInterpreter()
    try:
        with open(sys.argv[1]) as f:
            ast = parse_code(f.read())
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found")
        sys.exit(1)
    interpreter.load_program(ast)
    interpreter.run_program()