from experta import *
import time
import psutil


class Animal(Fact):
    """Fact representing an animal with an id, status, and step."""
    id = Field(str, mandatory=True)
    status = Field(str, mandatory=True)
    step = Field(int, mandatory=True)


class AnimalEngine(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        yield Animal(id="animal1", status="start", step=1)

    def add_fact(self, fact):
        """Adds a new fact to the system."""
        self.declare(fact)

    def remove_fact(self, fact_type):
        """Remove all facts of a specific type from the system."""
        to_remove = [fact for fact in self.facts.values() if isinstance(fact, fact_type)]
        for fact in to_remove:
            self.retract(fact)

    def update_fact(self, fact_type, **kwargs):
        """
        Updates facts of a specific type. If the fact exists, it's updated with provided keyword arguments;
        otherwise, a new fact is created and added to the system.
        """
        self.remove_fact(fact_type)  # First, remove all existing facts of this type
        new_fact = fact_type(**kwargs)  # Create a new fact instance with the updated information
        self.add_fact(new_fact)  # Add the new fact to the system


def generate_rules(num_rules):
    """Dynamically generates rules to add to the AnimalEngine."""

    def make_rule(i):
        @Rule(Animal(step=i))
        def rule(self):
            self.update_fact(Animal, id="animal1", step=i+1, status=f"process-{i + 1}")
        return rule

    for i in range(1, num_rules + 1):
        rule_name = f"step_{i}"
        setattr(AnimalEngine, rule_name, make_rule(i))


def run_engine(engine):
    process = psutil.Process()
    start_cpu = process.cpu_percent(interval=None)
    engine.reset()  # Prepare the engine for the execution.
    start_time = time.time()
    engine.run()  # Execute the rules.
    end_time = time.time()
    end_cpu = process.cpu_percent(interval=None)
    cpu_usage = (end_cpu - start_cpu) / psutil.cpu_count()
    memory_usage = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
    return end_time - start_time, cpu_usage, memory_usage


def main():
    number_of_rules = [10, 100, 1000]
    #number_of_rules = [10]
    executions = 20
    for num_rules in number_of_rules:
        generate_rules(num_rules)  # Generate the rules based on num_rules
        times, cpu_usages, memory_usages = [], [], []
        for _ in range(executions):
            engine = AnimalEngine()
            engine.reset()
            engine.declare(Animal(id="animal1", status="start", step=1))
            time_taken, cpu_usage, memory_usage = run_engine(engine)
            times.append(time_taken)
            cpu_usages.append(cpu_usage)
            memory_usages.append(memory_usage)

        average_time = sum(times) / executions
        average_cpu_usage = sum(cpu_usages) / executions
        average_memory_usage = sum(memory_usages) / executions - memory_usages[0]
        print(f"\nResults for {num_rules} rules:")
        print(f"Average Time Taken: {average_time} seconds")
        print(f"Average CPU Usage: {average_cpu_usage}%")
        print(f"Average Additional Memory Usage: {average_memory_usage} MB")


if __name__ == "__main__":
    main()
