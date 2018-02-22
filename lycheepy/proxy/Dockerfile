FROM nginx

ADD lycheepy /etc/nginx/sites-enabled/

RUN nginx -c /etc/nginx/sites-enabled/lycheepy -t

RUN service nginx reload

CMD ["nginx", "-g", "daemon off;"]
