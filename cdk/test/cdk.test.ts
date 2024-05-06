import * as cdk from 'aws-cdk-lib'
import { Template } from 'aws-cdk-lib/assertions'
import * as UIStack from '../lib/training-tracker-ui'
import * as TablesStack from '../lib/training-tracker-tables'
import * as ApiStack from '../lib/training-tracker-api'

test('Dynamo Tables stack', () => {
  const app = new cdk.App()
  // WHEN
  const stack = new TablesStack.TrainingSessionsTables(app, 'TrainingSessionsTablesStackTst')
  // THEN
  const template = Template.fromStack(stack)

  template.hasOutput('trainingSessionsTableArnTst', {})
})

test('UI stack', () => {
  const app = new cdk.App()
  // WHEN
  const stack = new UIStack.TrainingTrackerUi(app, 'UIStackTst')
  // THEN
  const template = Template.fromStack(stack)

  template.hasOutput('cloudFrontDomainNameTst', {})
})

test('API stack', () => {
  const app = new cdk.App()
  // WHEN
  const stack = new ApiStack.TrainingTrackerApi(app, 'APIStackTst')
  // THEN
  const template = Template.fromStack(stack)

  template.hasOutput('apiUrlTst', {})
})
