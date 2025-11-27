# ALX Project Nexus — Backend Engineering Documentation

## 📘 Overview

This repository serves as a comprehensive documentation hub for my learnings and experiences throughout the **ALX ProDev Backend Engineering Program**.  
It consolidates key backend concepts, technologies, challenges, and best practices I have mastered while building real-world projects and collaborating with peers.

The goal of this documentation is to:
- Showcase my understanding of backend development concepts and tools.
- Provide a reference guide for future learners.
- Encourage collaboration and knowledge sharing between backend and frontend developers.

---

## 🎯 Project Objective

**Project Nexus** aims to:
1. Consolidate and document core backend engineering learnings from the ALX ProDev curriculum.  
2. Demonstrate proficiency in backend frameworks, database design, and API development.  
3. Highlight personal challenges, solutions, and growth throughout the program.  
4. Serve as a collaborative knowledge base for both backend and frontend learners.

---

## 📊 Featured Project: Online Poll System

A production-ready Django REST API for creating polls, casting votes, and viewing real-time results with comprehensive Swagger documentation.

### Key Features
- 🗳️ **Poll Management** - Create polls with multiple options, set expiry dates (Admin only)
- 👥 **User Registration** - Email-based registration with password validation
- 🔐 **JWT Authentication** - Secure token-based authentication
- ✅ **Secure Voting** - Registered users can vote, with duplicate prevention
- 📊 **Real-Time Results** - Efficient vote counting with Redis caching
- 📚 **API Documentation** - Interactive Swagger/OpenAPI documentation
- 🔒 **Data Integrity** - Database-level constraints and validation
- 🛡️ **Rate Limiting** - API abuse prevention with configurable limits
- 🚀 **Production Ready** - Deployed on Render with PostgreSQL and Redis

### Live Demo
- **API Base URL:** `https://online-poll-system-scfg.onrender.com/api/`
- **Swagger Documentation:** `https://online-poll-system-scfg.onrender.com/api/docs/`
- **Admin Panel:** `https://online-poll-system-scfg.onrender.com/admin/`

### User Roles & Permissions
- **Anonymous Users** - Can view poll lists and results only
- **Registered Users** - Can register, login, vote, and view results
- **Admin Users** - Can create/delete polls, manage users, and access admin panel

### Tech Stack
- **Backend:** Django 5.0, Django REST Framework
- **Database:** PostgreSQL (Production), SQLite (Development)
- **Caching:** Redis (Upstash)
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Documentation:** drf-spectacular (Swagger/OpenAPI 3.0)
- **Rate Limiting:** django-ratelimit
- **Deployment:** Render
- **Version Control:** Git & GitHub

### API Endpoints

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|------------|
| **Authentication & User Management** |
| POST | `/api/auth/register/` | Register a new user account | No | No |
| POST | `/api/token/` | Login - obtain JWT access & refresh tokens | No | No |
| POST | `/api/token/refresh/` | Refresh access token | No | No |
| GET | `/api/auth/me/` | Get current user profile | Yes | No |
| PUT | `/api/auth/me/` | Update user profile | Yes | No |
| PATCH | `/api/auth/me/` | Partially update user profile | Yes | No |
| POST | `/api/auth/change-password/` | Change password | Yes | No |
| GET | `/api/auth/users/` | List all registered users | Yes | Yes |
| **Poll Management** |
| GET | `/api/polls/` | List all active polls | No | No |
| POST | `/api/polls/` | Create a new poll | Yes | Yes |
| GET | `/api/polls/{id}/` | Get poll details | No | No |
| **Voting** |
| POST | `/api/polls/{id}/vote/` | Cast a vote on a poll | Yes | No |
| GET | `/api/polls/{id}/results/` | View real-time poll results | No | No |
| **API Documentation** |
| GET | `/api/docs/` | Swagger UI documentation | No | No |
| GET | `/api/redoc/` | ReDoc documentation | No | No |
| GET | `/api/schema/` | OpenAPI schema (JSON/YAML) | No | No |

### Quick Start

#### Prerequisites
- Python 3.10+
- pip and virtualenv
- PostgreSQL (for production) or SQLite (for local development)

#### Local Installation

```bash
# Clone the repository
git clone https://github.com/DevPhil01/projectnexus.git
cd projectnexus/online_poll_system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DEBUG=True
SECRET_KEY=your-local-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
USE_SQLITE=True
EOF

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

#### Access Points
- **API:** http://127.0.0.1:8000/api/polls/
- **Swagger Docs:** http://127.0.0.1:8000/api/docs/
- **Admin Panel:** http://127.0.0.1:8000/admin/

### Usage Examples

#### 1. Register a New User
```bash
curl -X POST https://online-poll-system-scfg.onrender.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "message": "User registered successfully. Please login to get your access token."
}
```

#### 2. Login to Get JWT Token
```bash
curl -X POST https://online-poll-system-scfg.onrender.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 3. Get Your Profile
```bash
curl -X GET https://online-poll-system-scfg.onrender.com/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_admin": false,
  "date_joined": "2025-11-26T10:00:00Z"
}
```

#### 4. Create a Poll (Admin Only)
```bash
curl -X POST https://online-poll-system-scfg.onrender.com/api/polls/ \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Favorite Programming Language?",
    "description": "Vote for your favorite language",
    "expires_at": "2025-12-31T23:59:59Z",
    "options": ["Python", "JavaScript", "Go", "Rust"]
  }'
```

#### 5. Cast a Vote (Registered Users)
```bash
curl -X POST https://online-poll-system-scfg.onrender.com/api/polls/1/vote/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "poll": 1,
    "option": 2
  }'
```

#### 6. View Poll Results (Public)
```bash
curl https://online-poll-system-scfg.onrender.com/api/polls/1/results/
```

**Response:**
```json
{
  "poll": "Favorite Programming Language?",
  "total_votes": 45,
  "results": [
    {"option": "Python", "votes": 20},
    {"option": "JavaScript", "votes": 15},
    {"option": "Go", "votes": 7},
    {"option": "Rust", "votes": 3}
  ]
}
```

#### 7. Change Password
```bash
curl -X POST https://online-poll-system-scfg.onrender.com/api/auth/change-password/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass123!",
    "new_password": "NewSecurePass456!"
  }'
```

### Database Schema

#### Poll Model
```python
- id: Primary key
- title: Poll question (max 255 chars)
- description: Optional detailed description
- created_at: Auto-generated timestamp
- expires_at: Optional expiry datetime
- created_by: Foreign key to User
- is_active: Boolean flag for manual control
```

#### Option Model
```python
- id: Primary key
- poll: Foreign key to Poll
- text: Option text (max 255 chars)
- created_at: Auto-generated timestamp
```

#### Vote Model
```python
- id: Primary key
- poll: Foreign key to Poll
- option: Foreign key to Option
- user: Foreign key to User
- voted_at: Auto-generated timestamp
- Constraint: Unique(poll, user) - prevents duplicate voting
```

### Performance Optimizations
- ✅ Database indexes on frequently queried fields
- ✅ `prefetch_related()` to prevent N+1 queries
- ✅ Efficient vote counting with database aggregation
- ✅ Read-only serializers for list endpoints
- ✅ JWT token-based authentication (stateless)
- ✅ Redis caching for poll lists, details, and results
- ✅ Rate limiting on all endpoints to prevent abuse
- ✅ Cache invalidation on vote submission for real-time results

### Testing
Comprehensive testing performed using:
- **Postman** - Manual API endpoint testing
- **Swagger UI** - Interactive API exploration
- **Django Admin** - Data integrity verification

### Project Structure
```
online_poll_system/
├── manage.py
├── requirements.txt
├── build.sh
├── .env.example
├── .gitignore
├── README.md
├── online_poll_system/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── polls/
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── auth_serializers.py
    ├── views.py
    ├── auth_views.py
    ├── urls.py
    ├── auth_urls.py
    ├── admin.py
    └── migrations/
```

### Deployment

The application is deployed on Render with:
- PostgreSQL database
- Automatic deployments from GitHub
- Environment variables for configuration
- Static file serving with WhiteNoise

#### Deployment Steps
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Configure environment variables
5. Deploy automatically on push

### Git Commit Conventions
```bash
feat: add poll creation API
fix: resolve duplicate vote validation
perf: optimize vote counting queries
docs: update API documentation
chore: update dependencies
```

---

## 🧠 Major Learnings

### 1. Core Technologies

- **Python** — The primary programming language used to develop robust backend systems.
- **Django** — A high-level Python framework for building scalable web applications.
- **Django REST Framework (DRF)** — Used for creating RESTful APIs with serialization, authentication, and permission systems.
- **PostgreSQL** — A powerful relational database system with support for complex queries and relationships.
- **JWT Authentication** — Implemented token-based authentication for secure API access.
- **Swagger/OpenAPI** — Automated interactive API documentation for better developer experience.
- **Git & GitHub** — Version control and collaborative development workflows.

### 2. Key Backend Concepts

- **RESTful API Design:**  
  Built scalable, versioned, and well-documented REST APIs following HTTP methods and status code conventions.

- **Database Optimization:**  
  Learned normalization, indexing strategies, and query optimization to handle high-traffic scenarios efficiently.

- **Authentication & Authorization:**  
  Integrated JWT-based authentication and permission classes to secure endpoints.

- **Data Validation:**  
  Implemented comprehensive serializer validation to ensure data integrity at the API level.

- **User Management:**  
  Built complete user registration and authentication system with email-based accounts.

- **Role-Based Access Control:**  
  Implemented permission system to distinguish between admin and regular user capabilities.

- **API Documentation:**  
  Automated Swagger documentation generation for interactive API exploration and testing.

- **Caching Strategies:**  
  Implemented Redis caching to reduce database load and improve response times significantly.

- **Rate Limiting:**  
  Added API rate limiting to prevent abuse and ensure fair usage across all users.

- **Deployment:**  
  Deployed production-ready applications to cloud platforms with PostgreSQL databases.

---

## ⚙️ Challenges & Solutions

| Challenge | Description | Solution |
|------------|--------------|-----------|
| **Duplicate Voting** | Users could vote multiple times on same poll | Implemented database unique constraint on (user, poll) |
| **N+1 Query Problem** | Slow API responses when listing polls with options | Used `prefetch_related()` to optimize queries |
| **Token Authentication** | Securing API endpoints effectively | Integrated JWT with djangorestframework-simplejwt |
| **API Documentation** | Keeping documentation in sync with code | Used drf-spectacular for auto-generated Swagger docs |
| **Production Deployment** | Environment-specific configurations | Used python-decouple for environment variable management |
| **Vote Counting Performance** | Slow aggregation with growing data | Added database indexes and optimized count queries |
| **Redis Configuration** | Cache connection errors in production | Properly configured Upstash Redis with fallback to local cache |
| **Rate Limiting** | API abuse and spam voting | Implemented django-ratelimit with Redis backend |
| **Permission Management** | Unauthorized poll creation | Added role-based permissions (admin vs regular users) |

---

## 🧩 Best Practices & Takeaways

- Follow **Django design patterns** (Models-Views-Serializers) for clean architecture.
- Maintain **modular code** and use environment variables for configuration.
- Write **comprehensive documentation** for every API endpoint.
- Apply **database indexing** for frequently queried fields.
- Use **Git branching strategies** for clean version control.
- Implement **proper error handling** and validation at multiple layers.
- Prioritize **security and scalability** in every project.
- **Test thoroughly** before deployment using tools like Postman.

---

## 🤝 Collaboration

### Frontend Integration
This API is designed to be easily integrated with frontend applications:
- **Comprehensive Swagger documentation** for easy endpoint discovery
- **CORS-ready** (can be enabled in settings)
- **Consistent JSON responses** with proper error messages
- **JWT authentication** compatible with most frontend frameworks

### Collaborate With:
- **Frontend Developers:** to test API endpoints, improve integration, and ensure smooth data exchange.
- **Backend Peers:** to exchange ideas, debug issues, and share implementation strategies.

💡 *Tip:* Use the Swagger UI at `/api/docs/` for interactive API testing and integration!

---

## 📚 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [drf-spectacular Documentation](https://drf-spectacular.readthedocs.io/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Render Deployment Guide](https://render.com/docs)

---

## 🚀 Conclusion

The **ALX ProDev Backend Engineering Program** has been a transformative experience that deepened my understanding of backend technologies and real-world application development. The **Online Poll System** project demonstrates my ability to design, develop, test, and deploy production-ready APIs with best practices in mind.

This repository stands as a reflection of my journey, growth, and readiness to tackle production-grade backend challenges with confidence.

---

## 🏷️ Author

**Name:** Philip Oyoo  
**Program:** ALX ProDev Backend Engineering  
**GitHub:** [DevPhil01](https://github.com/DevPhil01)  



---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- ALX Africa for the comprehensive backend engineering curriculum
- The Django and DRF communities for excellent documentation
- Fellow ALX learners for collaboration and support

## NOTE
This is only the backend of the project. For full functionality, one needs to develop the front end section.
