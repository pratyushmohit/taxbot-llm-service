FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Install gunicorn and any other dependencies
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install pip, poetry, and any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.app:app"]
