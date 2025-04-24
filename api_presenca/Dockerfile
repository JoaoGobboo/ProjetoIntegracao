FROM python:3.9

# Definindo diretório de trabalho
WORKDIR /app

# Copiar o arquivo de dependências
COPY requirements.txt ./

# Instalar as dependências
RUN pip install -r requirements.txt

# Copiar o restante dos arquivos da aplicação
COPY . .

# Expor a porta
EXPOSE 5000

# Verificar se o Redis está pronto
HEALTHCHECK --interval=5s --timeout=3s --retries=5 \
  CMD redis-cli -h redis ping || exit 1

# Iniciar o servidor após garantir que o Redis está disponível
CMD python app.py
