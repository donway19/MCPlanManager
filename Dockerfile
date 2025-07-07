# Use an official Python runtime as a parent image, from a CN mirror
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the pre-built wheel from the dist directory
COPY dist/*.whl ./

# Install the wheel package. The wildcard will be expanded by the shell.
# This approach is faster and avoids including build dependencies in the final image.
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ ./*.whl

# Make port 6276 available, as specified in docker-compose.yml
EXPOSE 6276

# Set a default command, although it will be overridden by docker-compose.yml
CMD ["uvicorn", "mcplanmanager.app:mcp", "--host", "0.0.0.0", "--port", "6276"]