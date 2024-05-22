import { Duration, Stack } from 'aws-cdk-lib'
import { Architecture, Function, FunctionProps, Runtime } from 'aws-cdk-lib/aws-lambda'
import { PythonStack } from './python-stack'
import { kebab, snake, title } from './string-utils'

const DEFAULT_RUNTIME = Runtime.PYTHON_3_12
const DEFAULT_ARCHITECTURE = Architecture.ARM_64

/**
 * Create a Lambda function based on conventions: the module must have a handler function.
 * @param stack
 * @param name the Python module containing the lambda handler; should be in the top level package with the same name as the stack
 * @param env Dev or Prd
 * @param environment extra Lambda environment variables
 */
export function createPythonLambda(
  stack: PythonStack,
  name: string,
  env: string,
  environment: { [key: string]: string } = {},
): Function {
  const defaults: FunctionProps = {
    functionName: `${kebab(name)}${env}`,
    runtime: DEFAULT_RUNTIME,
    architecture: DEFAULT_ARCHITECTURE,
    timeout: Duration.seconds(90),
    memorySize: 1024,
    code: stack.createCodeAsset(),
    handler: `${snake(Stack.of(stack).stackName.slice(0, -6))}.${snake(name)}.handler`,
    layers: stack.lambdaLayers,
    environment: {
      ENVIRONMENT: env,
      LOG_LEVEL: 'INFO',
      POWERTOOLS_SERVICE_NAME: name,
      ...environment,
    },
    logRetention: stack.logRetention(),
  }

  const functionId = title(name) + 'Handler'
  return new Function(stack, functionId, { ...defaults })
}
