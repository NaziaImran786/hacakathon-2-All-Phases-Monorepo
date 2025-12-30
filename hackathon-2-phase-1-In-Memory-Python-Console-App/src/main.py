class TodoManager:
    """
    Manages the to-do list, including adding, viewing, updating, deleting, and marking tasks.
    """
    def __init__(self):
        """
        Initializes the TodoManager with an empty list of tasks and a starting ID of 1.
        """
        self.tasks = []
        self.next_id = 1

    def add_task(self, title, description):
        """
        Adds a new task to the list.

        Args:
            title (str): The title of the task.
            description (str): The description of the task.
        """
        task = {
            'id': self.next_id,
            'title': title,
            'description': description,
            'status': 'Pending'
        }
        self.tasks.append(task)
        self.next_id += 1
        print("Task added successfully.")

    def view_tasks(self):
        """
        Displays all tasks in a formatted table.
        """
        if not self.tasks:
            print("No tasks found.")
            return

        print("\n--- To-Do List ---")
        for task in self.tasks:
            status_marker = "[x]" if task['status'] == 'Completed' else "[ ]"
            print(f"{task['id']}. {status_marker} {task['title']} - {task['description']}")
        print("------------------")

    def update_task(self):
        """
        Updates a task's title and/or description based on user input.
        """
        try:
            task_id = int(input("Enter the ID of the task to update: "))
            task = next((t for t in self.tasks if t['id'] == task_id), None)

            if task is None:
                print("Error: Task not found.")
                return

            print(f"Updating Task {task_id}. Press Enter to keep the current value.")
            new_title = input(f"New Title ({task['title']}): ")
            new_description = input(f"New Description ({task['description']}): ")

            if new_title.strip():
                task['title'] = new_title
            if new_description.strip():
                task['description'] = new_description

            print("Task updated successfully.")
        except ValueError:
            print("Invalid input. Please enter a number for the Task ID.")

    def delete_task(self):
        """
        Deletes a task by its ID.
        """
        try:
            task_id = int(input("Enter the ID of the task to delete: "))
            task = next((t for t in self.tasks if t['id'] == task_id), None)

            if task is None:
                print("Error: Task not found.")
                return

            self.tasks.remove(task)
            print("Task deleted successfully.")
        except ValueError:
            print("Invalid input. Please enter a number for the Task ID.")

    def mark_complete(self):
        """
        Marks a task as 'Completed'.
        """
        try:
            task_id = int(input("Enter the ID of the task to mark as complete: "))
            task = next((t for t in self.tasks if t['id'] == task_id), None)

            if task is None:
                print("Error: Task not found.")
                return

            task['status'] = 'Completed'
            print("Task marked as complete.")
        except ValueError:
            print("Invalid input. Please enter a number for the Task ID.")

def main():
    """
    Main function to run the to-do application.
    """
    manager = TodoManager()

    while True:
        print("\nTodo App Menu:")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Mark Complete")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            title = input("Enter task title: ")
            description = input("Enter task description: ")
            if title and description:
                manager.add_task(title, description)
            else:
                print("Title and description cannot be empty.")
        elif choice == '2':
            manager.view_tasks()
        elif choice == '3':
            manager.update_task()
        elif choice == '4':
            manager.delete_task()
        elif choice == '5':
            manager.mark_complete()
        elif choice == '6':
            print("Exiting Todo App.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()