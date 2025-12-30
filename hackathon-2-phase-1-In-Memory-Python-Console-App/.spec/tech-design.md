# Technical Design Outline

## 1. Class Structure
*   **Task Model**: A `Task` model will be represented as a Python dictionary with the following keys:
    *   `id` (int): Unique auto-incrementing identifier.
    *   `title` (str): Title of the task.
    *   `description` (str): Description of the task.
    *   `status` (str): Current status of the task, defaulting to "Pending".

*   **TodoManager Class**: This class will encapsulate the application logic.
    *   `__init__(self)`: Initializes the `self.tasks` data structure and the `next_id` counter.
    *   `add_task(self, title, description)`: Adds a new task.
    *   `view_tasks(self)`: Returns a formatted list of all tasks.
    *   `update_task(self, task_id, title=None, description=None)`: Updates an existing task's title and/or description.
    *   `delete_task(self, task_id)`: Deletes a task by ID.
    *   `mark_complete(self, task_id)`: Changes a task's status to "Completed".

## 2. Main Loop (`main.py`)
The `main.py` entry point will contain a `while True` loop that presents a menu to the user.
1.  Initialize an instance of `TodoManager`.
2.  Display options (Add, View, Update, Delete, Mark Complete, Exit).
3.  Prompt the user for their choice.
4.  Based on the choice, call the appropriate `TodoManager` method.
5.  Handle user input for task details (title, description, ID).
6.  Implement error handling for invalid menu choices and invalid task IDs (e.g., non-integer input, non-existent IDs).
7.  The loop will exit when the user chooses the "Exit" option.

## 3. Data Structure
The tasks will be stored in-memory within the `TodoManager` class using a Python list of dictionaries.
`self.tasks = []`
A counter `self.next_id` will be used to assign unique IDs to new tasks.

## 4. Validation Strategy
*   **Menu Choice Validation**: User input for menu choices will be validated to ensure it corresponds to available options. Invalid choices will result in an error message and a re-display of the menu.
*   **Task ID Input Validation**:
    *   When the user enters a Task ID, the input will first be checked to ensure it's an integer.
    *   If not an integer, an appropriate error message will be displayed (e.g., "Invalid input. Please enter a number for the Task ID.").
    *   After successful integer conversion, the ID will be checked against the `self.tasks` list to confirm the task exists. If the ID does not exist, an error message will be displayed (e.g., "Task with ID [ID] not found.").
*   **Title/Description Input for Update**:
    *   For "Update Task", if the user provides an empty string for title or description, the original value will be retained as per requirements. We will consider an empty string (after stripping whitespace) as "empty input".