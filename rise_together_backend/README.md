# Rise Together Backend

Backend API for the Rise Together platform.

---

## Clone Repository

```bash
git clone https://github.com/joseph101kt/rise_together_barabari_project.git
cd rise_together_barabari_project
git checkout backend
git pull origin backend
```

---

## Create Virtual Environment

```bash
cd rise_together_backend

python -m venv .venv
```

### Activate

**Windows**

```bash
.venv\Scripts\activate
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file inside `rise_together_backend` and add the required environment variables.

---

## Run the Server

```bash
uvicorn main:app --reload
```

---

## API Documentation

Swagger UI

```
http://localhost:8000/docs
```

OpenAPI JSON

```
http://localhost:8000/openapi.json
```

---

## Testing Checklist

Verify the following API groups:

- Authentication
- Users
- Skills
- Modules
- User Modules

> **Note:** Logout is planned to be implemented in frontend (remove jwt and redirect to login page)