variable "function_name" {
  type    = string
  default = "LambdaDiscordOdinBot"
}

variable "github_repo_id" {
  type    = string
  default = "rafael-hiroshi/lambdadiscordodinbot"
}

variable "valheim_server_ecs_cluster_name" {
  type    = string
  default = "ValheimDedicatedServerCluster"
}

variable "valheim_server_ecs_service_name" {
  type    = string
  default = "ValheimService"
}

variable "valheim_container_ecs_name" {
  type    = string
  default = "ValheimServer"
}
