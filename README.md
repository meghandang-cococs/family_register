Contra Costa Chinese School Registration System (FastAPI Backend)

- Overview -
This project modernizes a legacy PHP-based school registration system by migrating it to a FastAPI, API-first backend. The original system (circa 2013) tightly coupled backend SQL logic with a server-rendered frontend, making it difficult to scale, maintain, or support modern clients.
The new backend cleanly separates concerns and provides a reusable REST API that supports the school’s existing registration workflows and enables future web and mobile frontends.
The system is used by 300+ families for student registration, class enrollment, payments, and volunteer tracking.

- Core Features -
Family & Account Management:
    - Supports existing families and new family onboarding
    - New families can:
        - Create an account
        - Enter familiy information
        - Add students (children) & student information
        - Edit information
    - Existing families can:
        - Log in and manage family and student records

Student Registration:
    - Each school term, parents can:
        - Register students for available classes
        - View current and past class enrollments
    - Registration workflows mirror legacy PHP behavior to ensure continuity

Records & History
    - Parents can view:
        - Past registrations
        - Payment history
        - Volunteer activity records

- System Architecture -
    - Backend Framework: FastAPI (Python)
    - Database: Existing SQL database (accessed via phpMyAdmin)
    - API Design:
        - RESTful endpoints
        - Modular router structure by domain:
            - family
            - student
            - registration
            - etc.
    - Data Validation:
        - Typed request/response schemas using Pydantic models
        - Schema definitions mirror existing database tables

- Migration Approach -
    - Analyzed the existing PHP codebase to understand:
        - Business logic
        - SQL queries
        - Registration workflows
    - Reverse-engineered legacy endpoints and recreated them in FastAPI
    - Preserved existing database structure and behavior to maintain data integrity
    - Incrementally validated functionality against the legacy system

- Testing & Documentation -
    - Interactive API documentation provided via Swagger UI / OpenAPI
    - Unit tests added to verify endpoint behavior and reduce regression risk
    - Version control managed with Git and GitHub

- Future Improvements -
    - Authentication and role-based access control
    - Frontend clients (web or mobile) consuming the same API
    - Improved reporting and admin tooling

- Author -
Meghan Dang 
(meghan-cococs, mdang2905, meghandang12)
www.linkedin.com/in/meghan-dang12 