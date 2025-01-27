data "aws_caller_identity" "current" {}

data "aws_ssm_parameter" "discord_public_key" {
  name = "/Applications/Discord/OdinBot/DiscordPublicKey"
}
