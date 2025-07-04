# Use an official Python runtime as a parent image, from a CN mirror
FROM docker.m.daocloud.io/library/python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files needed for installation
COPY pyproject.toml MANIFEST.in README.md LICENSE ./

# Copy the main application directory
COPY mcplanmanager ./mcplanmanager

# Install any needed packages specified in pyproject.toml
# This will install the project and its dependencies, including fastmcp
# and create the `mcplanmanager` command-line script.
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple .

# Copy the rest of the application
COPY . .

# Make port 8000 available to the world outside this container
# This is for the FastAPI server, although the default command runs SSE
EXPOSE 8000

# Run the MCP in SSE mode by default
CMD ["mcplanmanager"]
