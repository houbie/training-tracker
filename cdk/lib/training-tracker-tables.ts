import { Construct } from 'constructs'
import { CfnOutput, StackProps } from 'aws-cdk-lib'
import { AttributeType, BillingMode, Table } from 'aws-cdk-lib/aws-dynamodb'
import { EnvStack } from './common/env-stack'

export class TrainingTrackerTables extends EnvStack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props)

    const trainingSessionsTable = new Table(this, `trainingSessionsTable${this.env()}`, {
      tableName: `training-sessions-${this.env()}`,
      partitionKey: { name: 'id', type: AttributeType.STRING },
      billingMode: BillingMode.PROVISIONED,
      readCapacity: 1,
      writeCapacity: 1,
    })

    new CfnOutput(this, `trainingSessionsTableArn${this.env()}`, {
      value: trainingSessionsTable.tableArn,
      exportName: `trainingSessionsTableArn${this.env()}`,
    })
  }
}
