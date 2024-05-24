import * as fs from 'fs-extra'
import * as child_process from 'child_process'
import * as path from 'path'
import * as crypto from 'crypto'
import { StackProps } from 'aws-cdk-lib'
import { AssetCode, Code, LayerVersion } from 'aws-cdk-lib/aws-lambda'
import { Construct } from 'constructs'
import { EnvStack } from './env-stack'

/**
 * Stack that creates a common layer with all the dependencies for all Lambdas.
 * All Lambdas share the same code in the src directory, but can have different entry points.
 */
export class PythonStack extends EnvStack {
  public lambdaLayers: LayerVersion[]
  private readonly projectDir: string
  private readonly buildDir: string

  constructor(scope: Construct, constructId: string, props?: StackProps) {
    super(scope, constructId, props)

    this.projectDir = path.join('.', '..')
    this.buildDir = path.join('.', '../build')
    this.lambdaLayers = [this.createDependenciesLayer()]
  }

  createDependenciesLayer(): LayerVersion {
    const requirementsFile = path.join(this.projectDir, 'generated/requirements.txt')
    const requirements = fs.readFileSync(requirementsFile, {
      encoding: 'utf8',
    })
    const requirementsHash = crypto.createHash('md5').update(requirements).digest('hex')
    const destinationDir = path.join(this.buildDir, `layer-${requirementsHash}`)
    const pythonLibsDir = path.join(destinationDir, 'python')

    if (!fs.existsSync(pythonLibsDir)) {
      console.info('running pip install...')
      let result = child_process.spawnSync('pip3', [
        'install',
        '--no-deps',
        '--platform',
        'manylinux2014_aarch64',
        '--implementation',
        'cp',
        '--only-binary=:all:',
        '-r',
        requirementsFile.toString(),
        '-t',
        pythonLibsDir.toString(),
      ])
      if (result.status) {
        console.error(result.stderr.toString())
        throw new Error(`pip3 install exited with non-zero code: ${result.status}`)
      }
    }
    const layerId = `${this.stackName}-python-libs`
    const layerCode = Code.fromAsset(destinationDir)
    return new LayerVersion(this, layerId, { code: layerCode })
  }

  createCodeAsset(): AssetCode {
    const destinationDir = path.join(this.buildDir, 'src')
    fs.ensureDirSync(destinationDir)
    fs.copySync(path.join(this.projectDir, 'src'), destinationDir)
    fs.copySync(path.join(this.projectDir, 'openApi.yaml'), path.join(destinationDir, 'openApi.yaml'))
    return Code.fromAsset(destinationDir)
  }
}
