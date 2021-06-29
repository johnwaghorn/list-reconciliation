module "github_runner" {
  source = "git::https://git.digital.nhs.uk/SAWS/good-practice/terraform/github-runner.git?ref=main"

  product    = "list-reconciliation"
  maintainer = "SpinePod5"
  owner      = "SpinePod5"

  github_runner_config = {
    job_concurrency = 3
    instance_size   = "t3.medium"
    url             = "https://github.com/NHSDigital/list-reconciliation"
  }
}
