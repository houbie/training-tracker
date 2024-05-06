import { Stack } from 'aws-cdk-lib'
import { RetentionDays } from 'aws-cdk-lib/aws-logs'

export class EnvStack extends Stack {
  env() {
    return this.stackName.slice(-3)
  }

  isProd() {
    return this.env().toLowerCase() == 'prd'
  }

  logRetention() {
    return this.isProd() ? RetentionDays.ONE_MONTH : RetentionDays.ONE_WEEK
  }
}
