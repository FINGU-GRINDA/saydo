import type { CodegenConfig } from '@graphql-codegen/cli'

const config: CodegenConfig = {
  overwrite: true,
  schema: '../schema.graphql',
  documents: ['src/**/*.tsx', 'src/**/*.ts', 'app/**/*.tsx', 'app/**/*.ts', 'components/**/*.tsx', 'lib/**/*.ts'],
  generates: {
    'lib/generated/graphql.ts': {
      plugins: [
        'typescript',
        'typescript-operations',
        'typescript-react-query'
      ],
      config: {
        fetcher: '../api-client#apiClient',
        exposeFetcher: true,
        exposeQueryKeys: true,
        addInfiniteQuery: true,
        reactQueryVersion: 5,
        scalars: {
          DateTime: 'string',
          JSON: 'any'
        },
        namingConvention: {
          typeNames: 'pascal-case#pascalCase',
          enumValues: 'upper-case#upperCase'
        },
        hooks: {
          afterOneFileWrite: ['prettier --write']
        }
      }
    },
    'lib/generated/': {
      preset: 'client',
      plugins: [],
      config: {
        scalars: {
          DateTime: 'string',
          JSON: 'any'
        }
      }
    }
  },
  hooks: {
    afterAllFileWrite: ['prettier --write']
  }
}

export default config 