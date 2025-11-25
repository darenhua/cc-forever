FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    unzip \
    curl \
    python3-setuptools \
    npm \
    nodejs \
    docker.io \
    && apt-get clean

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Install process manager
RUN pip install supervisor
RUN npm install -g @anthropic-ai/claude-code

# Create supervisor directory
RUN mkdir -p /var/log/supervisor

# Copy application code
COPY backend /app/backend
COPY client /app/client

# Install Python dependencies
RUN pip install -r /app/backend/requirements.txt

# Install Node.js dependencies (if package.json exists)
COPY client/package*.json /app/client/
RUN cd /app/client && bun install

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000 9000 3001

# Start supervisor which manages both processes
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
