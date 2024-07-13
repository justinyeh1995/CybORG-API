{
  "name": "cyborg-web-interface",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "flask-dev": "FLASK_DEBUG=1 pip3 install -r requirements.txt && PYTHONPATH=./src/api/v1/CybORG python3 -m flask --app src/api/v1/CybORG/CybORG/Flask/flask_index run -p 5328",
    "fastapi-dev":"PYTHONPATH=./src/api/v1/CybORG uvicorn src.api.v1.CybORG.CybORG.FastAPI.fastapi_index:app --reload --port 8000",
    "next-dev": "next dev -p 8081",
    "dev": "concurrently \"npm run next-dev\" \"npm run fastapi-dev\"",
    "build": "next build",
    "start": "next start -p 8080",
    "lint": "next lint"
  },
  "dependencies": {
    "@emotion/react": "^11.11.3",
    "@emotion/styled": "^11.11.0",
    "next": "14.1.0",
    "react": "^18",
    "react-dom": "^18"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10.0.1",
    "concurrently": "^8.0.1",
    "eslint": "^8",
    "eslint-config-next": "14.1.0",
    "postcss": "^8",
    "tailwindcss": "^3.3.0",
    "typescript": "^5"
  }
}
