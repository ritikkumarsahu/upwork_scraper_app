# Base Image 
FROM python:3.8

# Working directory inside app
WORKDIR /app
#Copy the index.html file /usr/share/nginx/html/
COPY . .
# Install app dependecy 
RUN pip install -r requirements.txt
#Expose Port
EXPOSE 5000

CMD ["python","app.py"]