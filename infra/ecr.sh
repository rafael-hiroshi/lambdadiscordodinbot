# Authenticate Docker with AWS
aws ecr get-login-password --region sa-east-1 | docker login --username AWS --password-stdin 758724857051.dkr.ecr.sa-east-1.amazonaws.com

# Build the Docker image
docker build -t lambda-discord-odin-bot -f ../app/Dockerfile ../app

# Tag the image for ECR
docker tag lambda-discord-odin-bot:latest 758724857051.dkr.ecr.sa-east-1.amazonaws.com/lambda-discord-odin-bot-docker-repo:latest

# Push the image to ECR
docker push 758724857051.dkr.ecr.sa-east-1.amazonaws.com/lambda-discord-odin-bot-docker-repo:latest
