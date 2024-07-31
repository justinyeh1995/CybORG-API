# Project Planning for a potential polyglot microservice


<details>
<summary>Click to expand project structure</summary>
  
```
project-root/
├── .github/
├── api-gateway/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       └── index.js
├── auth-service/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       └── index.js
├── game-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       └── main.py
├── data-service/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       └── index.js
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── .gitignore
├── README.md
└── .env (optional, for local development)
```
</details>

<details>
## Directory Overview

- `api-gateway/`: API Gateway service (Node.js)
- `auth-service/`: Authentication service (Node.js)
- `game-service/`: Game logic service (Python)
- `data-service/`: Data management service (Node.js)
- `nginx/`: Nginx configuration for reverse proxy
- `docker-compose.yml`: Docker Compose configuration file
- `.gitignore`: Git ignore file
- `README.md`: Project documentation (this file)
- `.env`: Environment variables for local development (not tracked in git)
</details>


