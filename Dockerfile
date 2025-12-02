# BPM - Blood Pressure Monitoring Analysis Tool
# Docker image for running the GUI application

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV QT_QPA_PLATFORM=xcb
ENV QT_X11_NO_MITSHM=1

# Install system dependencies for Qt/PySide6
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Qt dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libegl1 \
    # X11 for GUI
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcb-glx0 \
    libxcb-keysyms1 \
    libxcb-image0 \
    libxcb-shm0 \
    libxcb-icccm4 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    # Fonts
    fonts-liberation \
    fonts-dejavu-core \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY resources/ ./resources/

# Create data directory for mounting
RUN mkdir -p /app/data

# Set the entrypoint
ENTRYPOINT ["python", "src/main.py"]
