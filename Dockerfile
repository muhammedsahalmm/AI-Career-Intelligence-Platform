# Base Image
# ----------------------------------------
FROM python:3.13-slim

# ----------------------------------------
# Prevent Python buffering
# ----------------------------------------
ENV PYTHONUNBUFFERED=1

# ----------------------------------------
# Working Directory
# ----------------------------------------
WORKDIR /app

# ----------------------------------------
# Install System Dependencies
# ----------------------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------
# Copy Requirements
# ----------------------------------------
COPY requirements.txt .

# ----------------------------------------
# Install CPU-only PyTorch
# ----------------------------------------
RUN pip install --no-cache-dir \
    torch==2.12.0 \
    --index-url https://download.pytorch.org/whl/cpu

# ----------------------------------------
# Install Remaining Python Packages
# ----------------------------------------
RUN pip install --no-cache-dir -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu

# ----------------------------------------
# Copy Project
# ----------------------------------------
COPY . .

# ----------------------------------------
# Expose Ports
# ----------------------------------------
EXPOSE 8000
EXPOSE 8501

# ----------------------------------------
# Run Streamlit
# ----------------------------------------
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]