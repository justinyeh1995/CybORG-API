# Set Ubuntu and Python versions from pre-built images
FROM ubuntu:22.10
FROM python:3.10

RUN apt-get update && apt-get install -y curl \
					 python-is-python3

# Install node version manager
RUN touch ~/.bashrc && chmod +x ~/.bashrc
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash
RUN bash -c "source ~/.nvm/nvm.sh && nvm install 20"

RUN bash -c "source ~/.nvm/nvm.sh && npm -v"

# Set working directory to /cage
WORKDIR /cage

# Copy local package requirements and init script into container's /cage folder
COPY . /cage

WORKDIR /cage/api/v1/CybORG

# Install packages
RUN pip install -e .

WORKDIR /cage

# Install packages
RUN pip install -r requirements.txt

CMD bash -c "source ~/.nvm/nvm.sh && npm run fastapi-dev"

