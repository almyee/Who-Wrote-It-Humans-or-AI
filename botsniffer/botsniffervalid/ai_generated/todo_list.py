import os

TODO_FILE = "todo_list.txt"

def load_tasks():
    """Loads tasks from the file."""
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r") as file:
        return [line.strip() for line in file.readlines()]

def save_tasks(tasks):
    """Saves tasks to the file."""
    with open(TODO_FILE, "w") as file:
        file.writelines(task + "\n" for task in tasks)

def add_task(task):
    """Adds a new task."""
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    print(f'Task added: "{task}"')

def list_tasks():
    """Lists all tasks."""
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
    else:
        print("To-Do List:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")

def remove_task(index):
    """Removes a task by index."""
    tasks = load_tasks()
    if 1 <= index <= len(tasks):
        removed = tasks.pop(index - 1)
        save_tasks(tasks)
        print(f'Task removed: "{removed}"')
    else:
        print("Invalid task number.")

def main():
    """Main loop for user interaction."""
    while True:
        print("\nOptions: add, list, remove, exit")
        command = input("Enter command: ").strip().lower()

        if command == "add":
            task = input("Enter task: ").strip()
            add_task(task)
        elif command == "list":
            list_tasks()
        elif command == "remove":
            try:
                index = int(input("Enter task number to remove: "))
                remove_task(index)
            except ValueError:
                print("Please enter a valid number.")
        elif command == "exit":
            print("Goodbye!")
            break
        else:
            print("Unknown command. Try again.")

if __name__ == "__main__":
    main()
