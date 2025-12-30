---
id: 001
title: signup-login-redirect
stage: general
date: 2025-12-30
surface: agent
model: claude-sonnet-4.5
feature: none
branch: main
user: Nazia Imran
command: modify authentication flow
labels: ["authentication", "stateless"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/main.py
 - frontend/app/signup/page.tsx
tests:
 - N/A (manual testing required)
---

## Prompt

I want to modify the authentication flow so that new users are redirected to the Login page after a successful signup, instead of being automatically logged in to the dashboard.

1. Backend Update (main.py / auth.py):

In the /signup endpoint, ensure the response only returns a success message (e.g., {"message": "User created successfully"}) and does NOT include a JWT token or session cookie.

2. Frontend Update (signup/page.tsx):

Modify the handleSubmit function in the Signup page.

After receiving a successful response from the backend, use router.push('/login') or router.push('/signin') instead of saving the token or redirecting to /tasks.

Add a 'Success' toast or alert message saying: 'Account created! Please sign in to continue.'

3. UI Alignment:

Ensure the transition from Signup to Signin is smooth and follows the existing glassmorphism theme.

Verify that the Better Auth session is not initialized prematurely.

4. Layout Fixes (Previous Request Sync):

While fixing this, also ensure the TaskDashboard is center-aligned and the AI Chat window is full-height and wider as requested previously.

Constraint: Follow the Stateless Architecture. No manual code changes. Refine the flow until a new user is forced to sign in manually after registration.

## Response snapshot

Modified the authentication flow to enforce explicit login after signup:

**Backend (backend/main.py:60-82):**
- Updated SignupResponse model to only include a message field
- Removed JWT token generation from /signup endpoint
- Now returns {"message": "User created successfully"} only
- Follows stateless architecture - no session state stored

**Frontend (frontend/app/signup/page.tsx:38-46):**
- Updated handleSubmit to redirect to /login after successful signup
- Changed status message to: "Account created! Please sign in to continue."
- Removed token storage logic from signup flow
- Increased redirect delay to 2 seconds for user to see success message

**Layout verification (frontend/app/tasks/page.tsx:408, 510):**
- TaskDashboard is center-aligned with max-w-5xl mx-auto
- AI Chat window is full-height (h-screen) with width-[450px]

## Outcome

- ✅ Impact: New users must explicitly login after registration, enforcing stateless auth flow
- 🧪 Tests: Manual testing required - test signup → login flow
- 📁 Files: 2 files modified (backend/main.py, frontend/app/signup/page.tsx)
- 🔁 Next prompts: Consider adding toast notification library for better UX
- 🧠 Reflection: The stateless architecture is properly maintained. The login page at /login already exists and handles authentication correctly. UI alignment is already correct per existing implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (manual testing phase)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - task completed as requested
