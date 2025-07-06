FROM python:3.10-slim

# Avoid interactive prompts during installs
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies required by some Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose Streamlit port (Cloud Run expects 8080)
EXPOSE 8080

# Streamlit run command
CMD ["streamlit", "run", "main.py", "--server.port=8080", "--server.enableCORS=false"]
