# Use a lightweight official Python runtime as a parent image
FROM python:3.11-slim

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install dependencies using uv into the system Python environment
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the application folder to /app/app
COPY app/ ./app/

# Run the CLI application when the container launches
CMD ["python", "-m", "app.main"]
