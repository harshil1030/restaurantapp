FROM python:3.11-slim

# Install ODBC Driver 17 and dependencies
RUN apt-get update && apt-get install -y \
    curl gnupg2 unixodbc-dev gcc g++ dos2unix \
    && mkdir -p /etc/apt/keyrings \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set workdir and copy files
WORKDIR /app
COPY . /app

# Convert .env to Unix format just in case (avoids line-ending issues)
#RUN dos2unix /app/.env

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# CMD to run the app
CMD ["python", "run.py"]
