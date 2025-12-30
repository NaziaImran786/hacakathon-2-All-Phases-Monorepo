# Project Tasks

This document outlines the key tasks for the project, categorized by functional area.

## T-001: Backend - Neon DB and SQLModel Setup

- **Objective:** Establish the database connection and define the data models using SQLModel for Neon DB.
- **Tasks:**
    - Initialize Neon DB connection within the FastAPI application.
    - Define core SQLModel models for entities like User, Todo, etc.
    - Implement database migration scripts for schema changes.
    - Develop repository layer for interacting with SQLModel models.
    - Write unit tests for database connection and model integrity.

## T-002: Backend - FastAPI JWT Middleware for Security

- **Objective:** Implement secure authentication and authorization using JWT tokens in FastAPI.
- **Tasks:**
    - Integrate `python-jose` or similar library for JWT encoding/decoding.
    - Create a JWT authentication middleware for FastAPI.
    - Implement token generation upon user login.
    - Develop token validation and user extraction logic.
    - Define role-based access control (RBAC) mechanisms.
    - Write integration tests for JWT authentication flow.

## T-003: Frontend - Better Auth Frontend Integration

- **Objective:** Enhance the user authentication experience in the Next.js frontend.
- **Tasks:**
    - Develop login and registration forms.
    - Implement secure storage of JWT tokens (e.g., HttpOnly cookies, localStorage with refresh token).
    - Create authentication context/provider for global state management.
    - Implement route guarding based on authentication status.
    - Add user session management (logout, token refresh).
    - Provide user feedback for authentication actions (loading states, error messages).

## T-004: Backend - CRUD API Endpoints with User Isolation

- **Objective:** Develop RESTful CRUD API endpoints for core resources, ensuring data isolation per user.
- **Tasks:**
    - Design API routes for Todo items (create, read, update, delete).
    - Implement business logic to associate Todo items with the authenticated user.
    - Ensure all data retrieval and modification operations respect user ownership.
    - Validate input data for all CRUD operations.
    - Implement pagination, sorting, and filtering for data retrieval.
    - Write end-to-end tests for CRUD operations with user isolation.

## T-005: Frontend - Next.js UI Development

- **Objective:** Develop the main user interface for the To-Do application using Next.js.
- **Tasks:**
    - Set up a new Next.js project.
    - Design and implement the main layout (header, navigation, footer).
    - Create a dashboard/main page to display user's To-Do list.
    - Develop components for displaying individual To-Do items.
    - Implement forms for adding and editing To-Do items.
    - Integrate API calls for CRUD operations with the UI.
    - Implement responsive design for various screen sizes.
    - Add basic styling and ensure a consistent look and feel.
    - Implement client-side routing.
    - Provide loading states and error handling feedback to the user.
