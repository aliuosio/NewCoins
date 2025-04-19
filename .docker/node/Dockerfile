# Dockerfile for Next.js frontend
FROM node:20-alpine
WORKDIR /app

# Copy only package.json and package-lock.json first for better caching
COPY package*.json ./

RUN npm install

# Copy the rest of your app
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
