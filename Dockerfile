# 1. Base Image: Use a lightweight Python version (Linux based)
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file first (for caching speed)
COPY requirements.txt .

# 4. Install dependencies
# We add --no-cache-dir to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code
COPY . .

# 6. Expose the port the app runs on
EXPOSE 8000

# 7. Command to run the application
# We use "0.0.0.0" to allow outside access to the container
CMD ["uvicorn", "src.main_api:app", "--host", "0.0.0.0", "--port", "8000"]