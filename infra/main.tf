terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket = "tfstate-758724857051"
    key    = "dev/resources/valheimserver.tfstate"
    region = "sa-east-1"
  }
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "LambdaDiscordOdinBotRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_cloudwatch_policy" {
  name        = "lambda_cloudwatch_policy"
  description = "IAM policy for Lambda to write logs to CloudWatch"
  path        = "/iamsr/"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_cloudwatch_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_cloudwatch_policy.arn
}

resource "aws_ecr_repository" "lambda_repository" {
  name = "lambda-discord-odin-bot-docker-repo"
}

resource "aws_lambda_function" "lambda_discord_bot" {
  function_name = "LambdaDiscordOdinBot"
  role          = aws_iam_role.lambda_execution_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repository.repository_url}:latest"

  environment {
    variables = {
      LOG_LEVEL = "info"
    }
  }

  tags = {
    Environment = "dev"
  }
}
