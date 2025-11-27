# Use the Playwright image
FROM mcr.microsoft.com/playwright/python:v1.55.0-noble

# Set the working directory in the container
WORKDIR /workspace

# Copy the current directory contents into the container at /workspace
COPY . /workspace

# 1. Install system-wide Python dependencies. 'playwright' will now be in /usr/local/bin
RUN pip install --no-cache-dir -r requirements.txt

# 2. Install the browser. This can now find the system-wide 'playwright' executable.
RUN playwright install msedge

# 3. Fix ownership of the application code AFTER all files are created.
RUN chown -R pwuser:pwuser /workspace

# 4. Switch to the non-root user for running the app.
USER pwuser

# Default command (can be overridden)
CMD ["python", "main.py"]