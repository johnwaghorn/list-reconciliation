module "lr_10_registration_orchestration" {
  source = "../../modules/step_function"

  name        = "lr-10-registration-orchestration"
  environment = local.environment

  lambdas_to_invoke = [
    module.lr_11_gp_registration_status.lambda.arn,
    module.lr_12_pds_registration_status.lambda.arn,
    module.lr_14_send_list_rec_results.lambda.arn,
    module.lr_15_process_demo_diffs.lambda.arn,
  ]

  step_function_definition = jsonencode({
    Comment = "lr-10-registration-orchestration",
    StartAt = "demographic_and_registration_outputs",
    States = {
      demographic_and_registration_outputs = {
        Type = "Parallel",
        Branches = [
          {
            StartAt = "invoke_lr_15_process_demo_diffs_lambda",
            States = {
              invoke_lr_15_process_demo_diffs_lambda = {
                Type      = "Task",
                Resource  = module.lr_15_process_demo_diffs.lambda.arn,
                InputPath = "$",
                End       = true,
              }
            }
          },
          {
            StartAt = "registration_outputs",
            States = {
              registration_outputs = {
                Type = "Parallel",
                End  = true,
                Branches = [
                  {
                    StartAt = "invoke_lr_11_gp_registration_status_lambda",
                    States = {
                      invoke_lr_11_gp_registration_status_lambda = {
                        Type      = "Task",
                        Resource  = module.lr_11_gp_registration_status.lambda.arn,
                        InputPath = "$",
                        End       = true,
                      }
                    },
                  },
                  {
                    StartAt = "invoke_lr_12_pds_registration_status_lambda",
                    States = {
                      invoke_lr_12_pds_registration_status_lambda = {
                        Type      = "Task",
                        Resource  = module.lr_12_pds_registration_status.lambda.arn,
                        InputPath = "$",
                        End       = true,
                      }
                    }
                  }
                ]
              }
            }
          }
        ],
        Next       = "invoke_lr_14_send_list_rec_results_lambda",
        ResultPath = null,
      },
      "invoke_lr_14_send_list_rec_results_lambda" = {
        Type      = "Task",
        Resource  = module.lr_14_send_list_rec_results.lambda.arn,
        InputPath = "$",
        End       = true,
      },
    },
  })
}
