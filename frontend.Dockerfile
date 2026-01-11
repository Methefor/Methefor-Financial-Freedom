# Node base image
FROM node:20-slim AS build

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy source
COPY frontend/ .

# Build
RUN npm run build

# Nginx to serve
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
