from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Union
from pprint import pprint

from CybORG.FastAPI import models
from CybORG.FastAPI.database import engine
from CybORG.FastAPI.api.main import api_router

# Create all tables
models.Base.metadata.create_all(bind=engine)

# Start main app
app = FastAPI()

# CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins (or use ["*"] for all)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include Routers
app.include_router(api_router, prefix="/api")

# Will be deprecated soon
@app.get("/", response_class=HTMLResponse)
def read_root():
    print("Hello FastAPI")
    return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Justin's Portfolio</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 0; box-sizing: border-box; }
                    .container { max-width: 800px; margin: auto; padding: 20px; }
                    header { text-align: center; padding: 50px 0; }
                    header h1 { margin: 0; }
                    section { margin-bottom: 40px; }
                    .projects img { max-width: 100%; height: auto; }
                    footer { background-color: #f3f3f3; text-align: center; padding: 20px 0; }
                </style>
            </head>
            <body>
                <header>
                    <h1>Justin Yeh🌳</h1>
                    <p>Welcome to my professional portfolio.</p>
                </header>
                
                <div class="container">
                    <section>
                        <h2>About Me</h2>
                        <p>Hello, I'm Justin Yeh(Madarin Name: 葉致廷 Yè Zhìtíng), a Master’s student in Computer Science at Vanderbilt University with a fervent interest in leveraging technology to solve complex problems, particularly within the realms of cybersecurity and data-driven applications. Check out some projects that I've done. Cheers, 🥂</p>
                    </section>
                    
                    <section>
                        <h2>Projects</h2>
                        <div class="projects">
                            <!-- Project 1 -->
                            <div class="project">
                                <h3>SolitaireJS.com</h3>
                                <img src="path_to_image" alt="Project Image">
                                <p>Description of your project. What was your role, what technologies did you use, and what was the outcome?</p>
                                <a href="https://solitairejs.com/" target="_blank">View Project</a>
                            </div>
                            
                            <!-- Project 2 -->
                            <div class="project">
                                <h3>iOS AR Visualization App</h3>
                                <img src="https://raw.githubusercontent.com/cage-challenge/cage-challenge-2/main/images/figure1.png" alt="Project Image">
                                <p>This App visulize the underlying network state of <a href="https://github.com/cage-challenge/cage-challenge-2" target="_blank">CybORG 2</a> in AR using SwiftUI, ARKit, RealityKit.</p>
                                <a href="https://github.com/justinyeh1995/CybORG-ARViz/" target="_blank">View Project</a>
                            </div>
                        </div>
                    </section>
                    
                    <section>
                        <h2>Contact</h2>
                        <p>Let people know how to get in touch with you. You can list your email address, LinkedIn profile, or other contact information here.</p>
                    </section>
                </div>
                
                <footer>
                    <p>&copy; 2024 Justin Yeh. All rights reserved.</p>
                </footer>
            </body>
            </html>
            """