import { CfnOutput, StackProps } from 'aws-cdk-lib'
import { LambdaIntegration } from 'aws-cdk-lib/aws-apigateway'
import { Table } from 'aws-cdk-lib/aws-dynamodb'
import { Construct } from 'constructs'
import { RestApiWithDefaults } from './common/api-gw'
import { createPythonLambda } from './common/lambda-function'
import { PythonStack } from './common/python-stack'

export class TrainingTrackerApi extends PythonStack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props)

    const trainingSessionsTable = Table.fromTableAttributes(this, `trainingSessions${this.env()}`, {
      tableName: `training-sessions-${this.env()}`,
    })

    const apiLambda = createPythonLambda(this, `ApiLambda`, this.env(), {
      TRAINING_SESSIONS_TABLE: trainingSessionsTable.tableName,
    })

    trainingSessionsTable.grantReadWriteData(apiLambda)

    const apiGw = new RestApiWithDefaults(this, `TrainingTrackerApi${this.env()}`, {
      throttlingRateLimit: 2,
      throttlingBurstLimit: 5,
    })

    apiGw.root.addProxy({
      defaultIntegration: new LambdaIntegration(apiLambda),
    })

    new CfnOutput(this, `apiUrl${this.env()}`, {
      value: apiGw.url,
      exportName: `apiUrl${this.env()}`,
    })
  }
}
