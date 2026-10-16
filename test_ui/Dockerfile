FROM node:22-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm install --no-audit --no-fund
COPY . .

ARG VITE_API_BASE=http://localhost:8000
ARG VITE_WS_URL=
ENV VITE_API_BASE=${VITE_API_BASE}
ENV VITE_WS_URL=${VITE_WS_URL}
RUN npm run build

FROM nginx:alpine AS runtime
RUN rm -f /etc/nginx/conf.d/default.conf \
    && printf '%s\n' \
      'server {' \
      '  listen 3030;' \
      '  listen [::]:3030;' \
      '  server_name _;' \
      '  root /usr/share/nginx/html;' \
      '  index index.html;' \
      '  server_tokens off;' \
      '  add_header X-Content-Type-Options nosniff always;' \
      '  add_header Referrer-Policy strict-origin-when-cross-origin always;' \
      '  location / {' \
      '    try_files $uri $uri/ /index.html;' \
      '  }' \
      '  location /assets/ {' \
      '    expires 1y;' \
      '    add_header Cache-Control "public, immutable";' \
      '    try_files $uri =404;' \
      '  }' \
      '}' > /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 3030
CMD ["nginx", "-g", "daemon off;"]
