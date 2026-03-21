FROM python:3.10-slim

# Install system dependencies if any are needed for Pillow/opencv (usually standard slim is fine for this app)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with user ID 1000 (standard for Hugging Face Spaces)
RUN useradd -m -u 1000 user

# Set working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY --chown=user:user . .

# Ensure the upload and instance directories exist and are writable
RUN mkdir -p static/uploads instance
RUN chmod -R 777 static/uploads instance

# Allow writing to the application directory so SQLite can create the database file
RUN chmod 777 .

# Switch to the non-root user
USER user

# Expose the default port used by Hugging Face Spaces
EXPOSE 7860

# Use Gunicorn to start the Flask application
# - 1 worker to save RAM (since the AI model loads in memory)
# - 120s timeout since AI generation may take longer than standard web requests
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "app:app"]
