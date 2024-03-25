import os
import time
import psutil
from clips import Environment

path_to_current_dir = os.path.dirname(__file__)
DEBUG = False

def setup_environment(env, num_rules):
    # Define the animal template directly
    env.build("""
    (deftemplate animal
        (slot id (type STRING))
        (slot status (type STRING))
        (slot step (type INTEGER)))
    """)
    generate_rules(env, num_rules)
    if DEBUG:
        env.eval('(watch facts)')
        env.eval('(watch rules)')
    env.reset()

def generate_rules(env, num_rules):
    for i in range(1, num_rules+1):  # Generates num_rules rules
        next_step = i + 1
        next_status = f"process-{next_step}" if i < 100 else "final"
        rule_string = f"""
        (defrule step{i}
            ?animal <- (animal (step {i}))
        =>
            (modify ?animal (step {next_step}) (status "{next_status}")))
        """
        env.build(rule_string)

def assert_initial_facts(env):
    env.assert_string('(animal (id "animal1") (status "start") (step 1))')

def run_engine(env):
    process = psutil.Process(os.getpid())
    start_cpu = process.cpu_percent(interval=None)
    start_time = time.time()
    env.run()
    end_time = time.time()
    end_cpu = process.cpu_percent(interval=None)
    cpu_usage = (end_cpu - start_cpu) / psutil.cpu_count()
    memory_usage = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
    return end_time - start_time, cpu_usage, memory_usage

def main():
    number_of_rules = [10, 100, 1000]
    executions = 20
    for num_rules in number_of_rules:
        times, cpu_usages, memory_usages = [], [], []
        for _ in range(executions):
            env = Environment()
            setup_environment(env, num_rules)
            assert_initial_facts(env)
            time_taken, cpu_usage, memory_usage = run_engine(env)
            times.append(time_taken)
            cpu_usages.append(cpu_usage)
            memory_usages.append(memory_usage)

        average_time = sum(times) / executions
        average_cpu_usage = sum(cpu_usages) / executions
        average_memory_usage = (sum(memory_usages) / executions) - memory_usages[0]
        print(f"\nResults for {num_rules} rules:")
        print(f"Average Time Taken: {average_time} seconds")
        print(f"Average CPU Usage: {average_cpu_usage}%")
        print(f"Average Additional Memory Usage: {average_memory_usage} MB")

if __name__ == "__main__":
    main()
