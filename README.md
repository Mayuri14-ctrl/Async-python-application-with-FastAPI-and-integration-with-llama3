# FastAPI Llama3 Integration

This repository contains a FastAPI application integrated with the Llama3 model to generate summaries for books and reviews.

## Features

- REST API for book and review management.
- Llama3 model integration for generating book summaries.

## Prerequisites

- AWS EC2 instance with Ubuntu AMI.
- Python 3.10 or later.
- PostgreSQL (optional, if using a relational database).

## Installation

### Local Setup

1.Create requirements file
```bash
pip freeze > requirements.txt
```
2. Push Code to GitHub:
```bash   
git init
git add main.py db/ requirements.txt
git commit -m "Initial commit with main.py and db setup"
git remote add origin https://github.com/Mayuri14-ctrl/Async-python-application-with-FastAPI-and-integration-with-llama3.git
git push -u origin master
```

##AWS EC2 Deployment
1.Launch EC2 Instance

Log into the AWS Management Console and navigate to EC2.
Launch a new instance with the following configurations:
AMI: Ubuntu 20.04 LTS.
Instance type: t2.micro (suitable for small-scale apps).
Configure a key pair for SSH access. It will download a pem file
Allow SSH, HTTP, and HTTPS traffic

2. SSH into the EC2 instance:
```bash   

cd Downloads
ssh -i "your_private_key.pem" ec2-user@your_public_ip_address

```

4. Clone the GitHub repository:
```bash   

https://github.com/Mayuri14-ctrl/Async-python-application-with-FastAPI-and-integration-with-llama3.git
cd Async-python-application-with-FastAPI-and-integration-with-llama3
```

6. Install python
```bash   

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.10-venv
sudo apt-get install python3.10-venv python3.10-distutils
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.10 get-pip.py
python3.10 -m venv myenv
source myenv/bin/activate
```

7. Install requirements
```bash   
pip install -r requirements.txt
pip install fastapi uvicorn sqlalchemy aiosqlite langchain_community
```

8. Install ollama and llama3
```bash   
sudo apt install snapd
sudo snap install ollama
ollama pull llama3
```

9. Deploying the API
```bash   
uvicorn main:app --host 0.0.0.0 --port 8000
```

10. FastAPI app accessible via HTTP (port 80),  Configure Nginx (Reverse Proxy)
```bash   
sudo apt-get install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
sudo nano /etc/nginx/sites-available/my_site
server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
sudo ln -s /etc/nginx/sites-available/my_site /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```   

Now, when you navigate to your EC2 instance’s public IP (http://34.203.193.16/), your FastAPI app should be accessible.






