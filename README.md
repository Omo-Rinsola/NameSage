# NameSage (Profile Intelligence Service)

A simple backend API that takes a name, gets basic information (gender, age, and country) from external APIs, stores the result in a database, and allows you to retrieve or manage the data.

---

##  Live API

Base URL:  
[link](https://hng-stage-0-gender-classifier-production-1330.up.railway.app)


---

## 🛠 Tech Stack

- FastAPI  
- SQLite  
- SQLAlchemy  
- httpx  

---

##  Run Locally

### 1. Clone the repository

```bash
git clone [enter git hub link]
cd profile-intelligence-service

```

### 2. Install dependencies

```bash
pip imstall -r requirements.txt
```

### 3. Run Server 
```bash
uvicorn main:app --reload 
```
