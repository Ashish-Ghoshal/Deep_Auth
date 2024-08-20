


# Face Authentication System

This project is an advanced Face Authentication System using MTCNN/Mediapipe for detection and FaceNet for embedding. It combines traditional and facial recognition methods for robust user validation. Deployed via Docker and Azure with CI/CD through GitHub Actions, the system features a Flask-based interface. 

## Project Archietecture
![Untitled Diagram drawio (1)](https://github.com/user-attachments/assets/9a4c4b56-f176-4803-a842-a7524d3a6269)

### Step 1: Recreate the Azure Virtual Machine
- Create the Virtual Machine:
- Go to the Azure Portal.
- Navigate to Virtual Machines > Create > Azure virtual machine.
#### Configure the VM:
- Image: Choose Ubuntu (latest version).
- Size: Select Standard_B2ms (2 vCPUs, 8 GB RAM) or another size based on your needs.
- Authentication: Use SSH public key or password for login (depending on your preference).
- Download the secret key when prompted and store it safely.
#### Networking:

   Go to network setting: Create Inbound Port Rule
   Add a rule to allow TCP traffic on port `8000` from `0.0.0.0/0` (or restrict to your IP for better security).

   ![image](https://github.com/user-attachments/assets/141ec866-6f2c-4e1a-9d6c-b012a2a1e885)


#### Review and Create: Verify the settings and click Create.
- Connect to the VM via SSH:
- After the VM is created, obtain the public IP address.
- Open your command prompt wherever you download your <file_name.pem> or cd to that location
- Once you are inside that directory run the below command
- username is the azure username and VM_IP_address is the VM's Public IP addrress
SSH into the VM:



```
ssh -i <file_name.pem> <username>@<VM_IP_Address>
```

### Step 2: Install and Set Up Docker
- Update and Install Docker:
Run the following commands on your VM:

```
sudo apt-get update -y
sudo apt-get upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### Step 3: Clone the GitHub Repository and Build Docker Image
Clone the Repository:
Clone the specific branch <branch-name>:

```
git clone -b <branch-name> https://github.com/YourUsername/YourRepository.git
cd YourRepository
```

#### Build the Docker Image:
- Build the Docker image with the required environment variables:

```
docker build -t face_auth \
  --build-arg SECRET_KEY=${{ secrets.SECRET_KEY }} \
  --build-arg ALGORITHM=${{ secrets.ALGORITHM }} \
  --build-arg MONGODB_URL_KEY=${{ secrets.MONGODB_URL_KEY }} \
  --build-arg DATABASE_NAME=${{ secrets.DATABASE_NAME }} \
  --build-arg USER_COLLECTION_NAME=${{ secrets.USER_COLLECTION_NAME }} \
  --build-arg EMBEDDING_COLLECTION_NAME=${{ secrets.EMBEDDING_COLLECTION_NAME }} .
```

### Step 4: Set Up Nginx for Domain and SSL (OPTIONAL)
- Install Nginx:
- Install and configure Nginx:

```
sudo apt-get install nginx -y
```

#### Configure Nginx for Your Domain:
- Open the Nginx configuration file:

```
sudo nano /etc/nginx/sites-available/default
```

 - Replace the content with:
nginx
```
server {
    listen 80;
    server_name <yourdomain> www.<yourdomain>;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Test and Reload Nginx:
- Test the configuration:

```
sudo nginx -t
```

- Reload Nginx:

```
sudo systemctl reload nginx
```

### Step 5: Obtain an SSL Certificate with Let’s Encrypt (OPTIONAL)
#### Install Certbot:
- Install Certbot for Nginx:

```
sudo apt-get install certbot python3-certbot-nginx -y
```

- Obtain SSL Certificate:
Run Certbot:

```
sudo certbot --nginx -d faceauth.online -d www.faceauth.online
```

Follow the prompts to complete the SSL installation. If Hostinger not configured properly follow the steps below.

### Steps to Update DNS Settings on Hostinger
#### Log in to Hostinger:
- Go to Hostinger and log in to your account.
#### Access the Domain Management Area:
- Once logged in, click on the “Domains” tab from the top menu.
- Find the domain yourdomain in your list of domains and click on Manage.
#### Navigate to DNS Settings:
- In the domain management screen, look for the “DNS/Nameservers” or “DNS Zone” section. This is where you can manage the DNS records for your domain.
#### Update the A Record:
- You need to update the A record so that it points to your Azure VM’s public IP address. You should have two A records:
- A Record for the root domain (yourdomain):
  
      Type: A
      Name/Host: @ (this represents the root domain)
      Points to: <Your_Azure_VM_Public_IP> (replace with your actual VM IP)
      TTL: Default (or 300 seconds)


- A Record for the www subdomain (www.yourdomain):
  
      Type: A
      Name/Host: www 
      Points to: <Your_Azure_VM_Public_IP> 
      TTL: Default (or 300 seconds)


#### Save Changes:
- After entering the correct IP address for both A records, save the changes.
#### Wait for DNS Propagation:
- DNS changes can take a few minutes to propagate across the internet, though sometimes it may take up to 24 hours. You can monitor the propagation using a tool like DNS Checker.
#### Verify the Configuration:
- Use DNS Checker to verify that yourdomain and www.yourdomain are both pointing to your Azure VM’s public IP address.
#### Re-run Certbot:
- Once DNS propagation is complete and your domain points to your Azure VM, SSH back into your Azure VM and run Certbot again:
bash

```
sudo certbot --nginx -d faceauth.online -d www.faceauth.online
```


### Step 6: Set Up GitHub Secrets for CI/CD
- Add GitHub Secrets:
- Go to your GitHub repository, navigate to Settings > Secrets and variables > Actions.
Add the following secrets:
- DOCKER_USERNAME: Your Docker Hub username.
- DOCKER_PASSWORD: Your Docker Hub password or access token.
- AZURE_VM_SSH_KEY: The private SSH key used to connect to the Azure VM.
- AZURE_VM_USERNAME: The username for the Azure VM.
- AZURE_VM_IP: The public IP address of the Azure VM.
- SECRET_KEY, ALGORITHM, MONGODB_URL_KEY, DATABASE_NAME, USER_COLLECTION_NAME, EMBEDDING_COLLECTION_NAME: The sensitive environment variables used by your application.

### Step 7: Set Up GitHub Actions for CI/CD
- Ensure the .github/workflows/docker-build.yml file contains the correct settings:
- Make sure the workflow is set to trigger on the <branch-name> branch:
yaml
```
on:
  push:
    branches:
      - <branch-name>
```

#### Trigger the Workflow:
Make changes or push to the <branch-name> branch to trigger the CI/CD pipeline:

```
git add .
git commit -m "Trigger CI/CD for deployment"
git push origin <branch-name>
```

### Step 8: Deploy the Docker Container
- Start the Docker Container:
- Ensure the container is running after the pipeline completes:

```
docker run -d -p 8000:8000 face_auth
```
If it doesn't work try:
```
docker run -d -p 8000:8000 --name face_auth \
  -e SECRET_KEY=<SECRET_KEY> \
  -e ALGORITHM=<ALGORITHM> \
  -e MONGODB_URL_KEY=<MONGODB_URL_KEY> \
  -e DATABASE_NAME=<DATABASE_NAME> \
  -e USER_COLLECTION_NAME=<USER_COLLECTION_NAME> \
  -e EMBEDDING_COLLECTION_NAME=<EMBEDDING_COLLECTION_NAME> \
  face_auth
```


### Step 9: Access Your Application Securely
Open Your Browser:
- Visit https://yourdomain:8000 to ensure everything is working correctly.






