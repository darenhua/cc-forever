FROM python:3.12-slim-trixie

# Install system dependencies including setuptools
RUN apt-get update && apt-get install -y \
    curl \
    python3-setuptools \
    npm \
    && apt-get clean

# Install Docker CLI
RUN apt-get update && apt-get install -y \
    docker.io \
    && apt-get clean

# Install setuptools via pip as well
RUN pip install setuptools

# Copy your application
COPY /backend .

# Install Python dependencies
RUN pip install -r requirements.txt
RUN npm install -g @anthropic-ai/claude-code

EXPOSE 8000
EXPOSE 9000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
