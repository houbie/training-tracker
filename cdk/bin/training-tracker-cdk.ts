#!/usr/bin/env node
import 'source-map-support/register'
import {TrainingTrackerApi} from '../lib/training-tracker-api'
import {TrainingTrackerUi} from '../lib/training-tracker-ui'
import {App} from 'aws-cdk-lib'
import {TrainingTrackerTables} from '../lib/training-tracker-tables'

const app = new App()

const ENV = app.node.tryGetContext('env') || 'V1a'

new TrainingTrackerTables(app, `TrainingTrackerTables${ENV}`, {
    env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
})

new TrainingTrackerApi(app, `TrainingTrackerApi${ENV}`, {
    env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
})

new TrainingTrackerUi(app, `TrainingTrackerUI${ENV}`, {
    env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
})
