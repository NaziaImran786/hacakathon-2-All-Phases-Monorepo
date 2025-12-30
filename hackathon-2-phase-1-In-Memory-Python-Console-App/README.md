# Evolution of Todo - Phase 1

## Description
This is a Python console application representing "Phase 1" of the Evolution of Todo project. It is built following Spec-Driven Development principles, focusing on an in-memory task management system.

## Features
The application provides the following core functionalities:
1.  **Add Task**: Allows users to add new tasks with a title and description. Tasks are automatically assigned a unique ID and a "Pending" status.
2.  **View Tasks**: Displays all current tasks in a formatted list, showing ID, status (Pending/Completed), title, and description.
3.  **Update Task**: Enables users to modify the title and/or description of an existing task using its ID. Existing values are retained if no new input is provided.
4.  **Delete Task**: Permanently removes a task from the list using its ID.
5.  **Mark Complete**: Changes the status of a specified task from "Pending" to "Completed".

## How to Run
To run this application, ensure you have Python 3.13+ installed on your system.

1.  **Install Python**: If you don't have Python 3.13+ installed, please download it from the official Python website.
2.  **Navigate to the project directory**:
    ```bash
    cd /path/to/your/todo-app
    ```
3.  **Run the application**:
    ```bash
    python src/main.py
    ```

## Project Structure
```
.
├── .spec/
├── src/
└── README.md
```

## Spec-Driven Process
This application was developed using Spec-Kit principles, guided by a Gemini Agent. The development process involved clear specifications for requirements and technical design, which were then implemented and iterated upon.
