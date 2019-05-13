import time


class TimeHandler:
    last_time = 0
    id_stack = []

    function_times = {}

    total_time = 0
    min_percentage = 0.01

    def start_timing(self, new_id):
        new_time = time.time()
        if len(self.function_times) > 0:
            if self.id_stack[-1] is new_id:
                print(new_id, "is already being timed.")
                return

            delta_time = new_time - self.last_time
            self.add_time(self.id_stack[-1], delta_time)

        self.last_time = new_time
        self.id_stack.append(new_id)

    def end_timing(self, func_id):
        if self.id_stack[-1] is not func_id:
            print("Timing of {} was unresolved".format(self.id_stack[-1]))
            return

        new_time = time.time()
        self.add_time(self.id_stack.pop(-1), new_time - self.last_time)
        self.last_time = new_time

    def add_time(self, func_id, delta_time):
        if func_id in self.function_times:
            self.function_times[func_id] = self.function_times.get(func_id) + delta_time
        else:
            self.function_times[func_id] = delta_time

    def print_report(self):
        for i, t in self.function_times.items():
            print("{}: {}".format(round(t, 2), i))
