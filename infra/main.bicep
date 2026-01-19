// ===========================================
// EcoSort-AI Infrastructure - Main Bicep Template
// ===========================================
// Deploys Azure Static Web App and Key Vault

// ---- Parameters ----

@description('Environment name for resource naming')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'prod'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Project name used for resource naming')
param projectName string = 'ecosort'

@description('Tags to apply to all resources')
param tags object = {
  Project: 'EcoSort-AI'
  Environment: environment
  ManagedBy: 'Bicep'
}

@description('SKU for Static Web App')
@allowed(['Free', 'Standard'])
param staticWebAppSku string = 'Standard'

@description('Enable Key Vault soft delete')
param enableSoftDelete bool = true

@description('Soft delete retention in days')
@minValue(7)
@maxValue(90)
param softDeleteRetentionDays int = 90

// ---- Variables ----

var resourceSuffix = '${projectName}-${environment}-${uniqueString(resourceGroup().id)}'
var staticWebAppName = 'swa-${resourceSuffix}'
var keyVaultName = 'kv-${take(resourceSuffix, 20)}'

// ---- Resources ----

// Azure Static Web App
module staticWebApp 'br/public:avm/res/web/static-site:0.6.0' = {
  name: 'staticWebAppDeployment'
  params: {
    name: staticWebAppName
    location: location
    tags: tags
    sku: staticWebAppSku
    stagingEnvironmentPolicy: 'Enabled'
    allowConfigFileUpdates: true
    enterpriseGradeCdnStatus: 'Disabled'
    publicNetworkAccess: 'Enabled'
  }
}

// Azure Key Vault
module keyVault 'br/public:avm/res/key-vault/vault:0.11.0' = {
  name: 'keyVaultDeployment'
  params: {
    name: keyVaultName
    location: location
    tags: tags
    enableRbacAuthorization: true
    enableSoftDelete: enableSoftDelete
    softDeleteRetentionInDays: softDeleteRetentionDays
    enablePurgeProtection: environment == 'prod'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

// ---- Outputs ----

@description('Static Web App name')
output staticWebAppName string = staticWebApp.outputs.name

@description('Static Web App default hostname')
output staticWebAppUrl string = staticWebApp.outputs.defaultHostname

@description('Static Web App resource ID')
output staticWebAppResourceId string = staticWebApp.outputs.resourceId

@description('Key Vault name')
output keyVaultName string = keyVault.outputs.name

@description('Key Vault URI')
output keyVaultUri string = keyVault.outputs.uri

@description('Key Vault resource ID')
output keyVaultResourceId string = keyVault.outputs.resourceId

@description('Resource group name')
output resourceGroupName string = resourceGroup().name
