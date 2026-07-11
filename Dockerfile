FROM python:3.11-slim

# Evitar gravação de bytecode .pyc e garantir output direto no console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código
COPY . .

# Comando para rodar a aplicação
CMD ["python", "main.py"]
