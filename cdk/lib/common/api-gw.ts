import {
  AccessLogFormat,
  EndpointType,
  LogGroupLogDestination,
  RestApi,
  RestApiProps,
} from 'aws-cdk-lib/aws-apigateway'
import { LogGroup } from 'aws-cdk-lib/aws-logs'
import { EnvStack } from './env-stack'

export class RestApiWithDefaults extends RestApi {
  constructor(stack: EnvStack, construct_id: string, props?: RestApiProps) {
    const logGroup = new LogGroup(stack, `${construct_id}LogGroup`, {
      retention: stack.logRetention(),
    })

    super(stack, construct_id, {
      endpointConfiguration: {
        types: [EndpointType.REGIONAL],
        ...props?.endpointConfiguration,
      },
      domainName: props?.domainName,
      cloudWatchRole: true,
      deployOptions: {
        accessLogDestination: new LogGroupLogDestination(logGroup),
        accessLogFormat: AccessLogFormat.jsonWithStandardFields(),
      },
    })
  }
}
