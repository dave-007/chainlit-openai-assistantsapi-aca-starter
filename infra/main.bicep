targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

param chainlitExists bool

@secure()
@minLength(1)
@description('OpenAI API Key to use')
param openAiApiKey string

@secure()
@minLength(1)
@description('OpenAI Assistant ID to use')
param openAssistantId string

@secure()
@minLength(1)
@description('Chainlit Auth Secret')
param chainlistAuthSecret string

@minLength(1)
@description('Entra ID Tenant Id')
param entraIdTenantId string

@minLength(1)
@description('Entra ID App Registration Client Id')
param entraIdClientId string

@secure()
@minLength(1)
@description('Entra ID App Registration Secret')
param entraIdClientSecret string

@secure()
@minLength(1)
@description('Database Connection String')
param databaseConnectionString string

@minLength(1)
@description('Storage Account Name')
param storageAccountName string

@minLength(1)
@description('Storage Container Name')
param containerName string

@secure()
@minLength(1)
@description('Storage Access Key')
param storageAccessKey string

@secure()
@minLength(1)
@description('Storage Connection String')
param storageConnectionString string

var openAIKeysDefinition = {
  settings: [
    {
      name: 'OPENAI_API_KEY'
      secret: true
      value: openAiApiKey
    }
    {
      name: 'OPENAI_ASSISTANT_ID'
      secret: true
      value: openAssistantId
    }
    {
      name: 'CHAINLIT_AUTH_SECRET'
      secret: true
      value: chainlistAuthSecret
    }
    {
      name: 'OAUTH_AZURE_AD_CLIENT_SECRET'
      secret: true
      value: entraIdClientSecret
    }
    {
      name: 'DATABASE_URL'
      secret: true
      value: databaseConnectionString
    }
    {
      name: 'APP_AZURE_STORAGE_ACCESS_KEY'
      secret: true
      value: storageAccessKey
    }
    {
      name: 'APP_AZURE_STORAGE_CONNECTION_STRING'
      secret: true
      value: storageConnectionString
    }
  ]
}

@description('Id of the user or app to assign application roles')
param principalId string

// Tags that should be applied to all resources.
// 
// Note that 'azd-service-name' tags should be applied separately to service host resources.
// Example usage:
//   tags: union(tags, { 'azd-service-name': <service name in azure.yaml> })
var tags = {
  'azd-env-name': environmentName
}

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

module resources 'resources.bicep' = {
  scope: rg
  name: 'resources'
  params: {
    location: location
    tags: tags
    principalId: principalId
    chainlitExists: chainlitExists
    openAIKeysDefinition: openAIKeysDefinition
    entraIdTenantId: entraIdTenantId
    entraIdClientId: entraIdClientId
    storageAccountName: storageAccountName
    containerName: containerName
  }
}
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = resources.outputs.AZURE_CONTAINER_REGISTRY_ENDPOINT
output AZURE_KEY_VAULT_ENDPOINT string = resources.outputs.AZURE_KEY_VAULT_ENDPOINT
output AZURE_KEY_VAULT_NAME string = resources.outputs.AZURE_KEY_VAULT_NAME
output AZURE_RESOURCE_SRC_ID string = resources.outputs.AZURE_RESOURCE_SRC_ID
