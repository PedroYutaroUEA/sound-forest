
FROM python:3.9-slim

# diretório de trabalho dentro do contêiner
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# porta que o servidor vai usar (padrão do flask)
EXPOSE 5000

# Comando para rodar a aplicação quando o contêiner for iniciado
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
