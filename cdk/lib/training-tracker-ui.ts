import { CfnOutput, RemovalPolicy, StackProps } from 'aws-cdk-lib'
import { CloudFrontAllowedMethods, CloudFrontWebDistribution, OriginAccessIdentity } from 'aws-cdk-lib/aws-cloudfront'
import { PolicyStatement } from 'aws-cdk-lib/aws-iam'
import { BlockPublicAccess, Bucket, BucketEncryption, BucketPolicy } from 'aws-cdk-lib/aws-s3'
import { BucketDeployment, CacheControl, Source } from 'aws-cdk-lib/aws-s3-deployment'
import { Construct } from 'constructs'
import * as path from 'path'
import { EnvStack } from './common/env-stack'

export class TrainingTrackerUi extends EnvStack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props)

    const bucket = new Bucket(this, `uiBucket`, {
      bucketName: `training-tracker-ui-${this.env().toLowerCase()}-${this.region}`,
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      encryption: BucketEncryption.S3_MANAGED,
      enforceSSL: true,
    })

    new BucketDeployment(this, 'indexBucketDeployment', {
      destinationBucket: bucket,
      sources: [Source.asset(path.join('.', '../ui/build'))],
      include: ['index.html', 'asset-manifest.json'],
      cacheControl: [CacheControl.fromString('max-age=0,no-cache,no-store,must-revalidate')],
    })

    new BucketDeployment(this, 'bucketDeployment', {
      destinationBucket: bucket,
      sources: [Source.asset(path.join('.', '../ui/build'))],
      exclude: ['index.html'],
      cacheControl: [CacheControl.fromString('public,max-age=31536000,immutable')],
    })

    const cloudFrontOAI = new OriginAccessIdentity(this, 'cloudfrontOai')
    // Explicitly add Bucket Policy
    const policyStatement = new PolicyStatement()
    policyStatement.addActions('s3:GetObject')
    policyStatement.addActions('s3:ListBucket') // with S3 bucket returns 404 for not found instead of 403
    policyStatement.addResources(bucket.bucketArn)
    policyStatement.addResources(`${bucket.bucketArn}/*`)
    policyStatement.addCanonicalUserPrincipal(cloudFrontOAI.cloudFrontOriginAccessIdentityS3CanonicalUserId)
    // Manually create or update bucket policy
    if (!bucket.policy) {
      new BucketPolicy(this, 'Policy', { bucket }).document.addStatements(policyStatement)
    } else {
      bucket.policy.document.addStatements(policyStatement)
    }

    const cloudFrontWebDistribution = new CloudFrontWebDistribution(this, 'BackendCF', {
      originConfigs: [
        {
          s3OriginSource: {
            s3BucketSource: bucket,
            originAccessIdentity: cloudFrontOAI,
          },
          behaviors: [
            { isDefaultBehavior: true },
            { pathPattern: '/*', allowedMethods: CloudFrontAllowedMethods.GET_HEAD },
          ],
        },
      ],
    })
    new CfnOutput(this, `cloudFrontDomainName${this.env()}`, {
      value: cloudFrontWebDistribution.distributionDomainName,
    })
  }
}
