FROM node:18

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar o restante dos arquivos da aplicação
COPY . .

# Expor a porta 3000
EXPOSE 3000

# Verificar se o Redis está pronto
HEALTHCHECK --interval=5s --timeout=3s --retries=5 \
  CMD redis-cli -h redis ping || exit 1

# Iniciar o servidor após garantir que o Redis está disponível
CMD node app.js
