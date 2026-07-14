FROM nginx:alpine

LABEL name="Adnan Khan"
LABEL description="TriageFlow Frontend"

# Copy frontend files into nginx's default serving directory
COPY . /usr/share/nginx/html

# Override nginx config to proxy API calls to the backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]