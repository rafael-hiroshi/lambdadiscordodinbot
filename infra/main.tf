terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket = "tfstate-758724857051"
    key    = "lambdadiscordodinbot.tfstate"
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

  tags = {
    GITHUB_REPO_ID = var.github_repo_id
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "lambda_policy"
  description = "IAM policy for Lambda execution"
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
      },
      {
        Effect = "Allow",
        Action = [
          "ecs:DescribeServices",
          "ecs:UpdateService",
          "ecs:ExecuteCommand",
          "ecs:ListTasks"
        ],
        Resource = [
          "arn:aws:ecs:sa-east-1:${data.aws_caller_identity.current.account_id}:service/${var.valheim_server_ecs_cluster_name}/*",
          "arn:aws:ecs:sa-east-1:${data.aws_caller_identity.current.account_id}:container-instance/${var.valheim_server_ecs_cluster_name}/*",
          "arn:aws:ecs:sa-east-1:${data.aws_caller_identity.current.account_id}:cluster/${var.valheim_server_ecs_cluster_name}",
          "arn:aws:ecs:sa-east-1:${data.aws_caller_identity.current.account_id}:task/${var.valheim_server_ecs_cluster_name}/*",
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ],
        "Resource" : "*"
      }
    ]
  })

  tags = {
    GITHUB_REPO_ID = var.github_repo_id
  }
}


resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_ecr_repository" "lambda_repository" {
  name         = "lambda-discord-odin-bot-docker-repo"
  force_delete = true
}

# Null Resource to push docker image to ECR
resource "null_resource" "push_ecr_image" {
  provisioner "local-exec" {
    command = "./ecr.sh"
  }

  triggers = {
    ecr_push_time = timestamp() # Forces re-execution when this value changes
  }
}

resource "aws_lambda_function" "lambda_discord_bot" {
  function_name = var.function_name
  role          = aws_iam_role.lambda_execution_role.arn
  package_type  = "Image"
  timeout       = 30
  image_uri     = "${aws_ecr_repository.lambda_repository.repository_url}@${data.aws_ecr_image.lambda_image.image_digest}"

  environment {
    variables = {
      LOG_LEVEL                  = "info",
      DISCORD_PUBLIC_KEY         = data.aws_ssm_parameter.discord_public_key.value,
      VALHEIM_SERVER_ECS_CLUSTER = var.valheim_server_ecs_cluster_name,
      VALHEIM_SERVER_ECS_SERVICE = var.valheim_server_ecs_service_name,
      VALHEIM_CONTAINER_NAME     = var.valheim_container_ecs_name
    }
  }

  tags = {
    GITHUB_REPO_ID = var.github_repo_id
  }

  # Ensure Lambda function is recreated when the image changes
  lifecycle {
    create_before_destroy = true
  }

  depends_on = [aws_cloudwatch_log_group.lambda_log_group]
}

# Data Source for Latest ECR Image Digest
data "aws_ecr_image" "lambda_image" {
  repository_name = aws_ecr_repository.lambda_repository.name
  image_tag = "latest"

  # Forces update when a new image is pushed
  depends_on = [null_resource.push_ecr_image]
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 30

  tags = {
    GITHUB_REPO_ID = var.github_repo_id
  }
}

resource "aws_lambda_function_url" "lambda_function_url" {
  function_name      = aws_lambda_function.lambda_discord_bot.function_name
  authorization_type = "NONE"

  cors {
    allow_origins = ["*"]
    allow_methods = ["POST"]
  }
}

# Allow public access to the Lambda function via the function URL
resource "aws_lambda_permission" "allow_public_access" {
  statement_id           = "FunctionURLAllowPublicAccess"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.lambda_discord_bot.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

output "lambda_function_url" {
  value = aws_lambda_function_url.lambda_function_url.function_url
}

resource "aws_ecr_lifecycle_policy" "latest_image_policy" {
  repository = aws_ecr_repository.lambda_repository.name

  policy = jsonencode({
    "rules" = [
      {
        "rulePriority" = 1
        "description"  = "Keep only the latest image"
        "selection" = {
          "tagStatus"   = "any"
          "countType"   = "imageCountMoreThan"
          "countNumber" = 1
        }
        "action" = {
          "type" = "expire"
        }
      }
    ]
  })
}
