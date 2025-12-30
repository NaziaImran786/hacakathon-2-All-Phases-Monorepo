## Core Features
1. **Add Task**:
   - User inputs Title and Description.
   - System assigns a unique auto-incrementing ID.
   - Status defaults to "Pending".

2. **View Tasks**:
   - Display a formatted table/list of all tasks.
   - Columns: [ID] [Status] Title - Description.
   - If list is empty, show "No tasks found".

3. **Update Task**:
   - User enters Task ID.
   - User can update Title and/or Description.
   - Keep original values if input is empty.

4. **Delete Task**:
   - User enters Task ID.
   - Task is permanently removed from memory.
   - Show error if ID does not exist.

5. **Mark Complete**:
   - User enters Task ID.
   - Status changes from "Pending" to "Completed".
   - Completed tasks should be visually distinct (e.g., using [x]).

## System Constraints
- App must run continuously until the user chooses "Exit".
