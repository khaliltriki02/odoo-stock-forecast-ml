FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer la version EXACTE de cmdstan attendue par Prophet, au bon endroit
RUN python -c "import cmdstanpy; cmdstanpy.install_cmdstan(version='2.33.1', dir='/usr/local/lib/python3.11/site-packages/prophet/stan_model', overwrite=True)"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]