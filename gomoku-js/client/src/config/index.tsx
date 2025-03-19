import { baseSepolia } from '@reown/appkit/networks'
import type { AppKitNetwork } from '@reown/appkit/networks'
import { defineChain } from '@reown/appkit/networks'
import { EthersAdapter } from '@reown/appkit-adapter-ethers'

// Get projectId from https://cloud.reown.com
export const projectId = import.meta.env.VITE_PROJECT_ID

if (!projectId) {
  throw new Error('Project ID is not defined')
}

export const metadata = {
  name: 'Sparsity-Gomoku',
  description: 'Sparsity Gomoku Demo',
  url: 'https://reown.com/appkit', // origin must match your domain & subdomain
  icons: ['https://assets.reown.com/reown-profile-pic.png'],
}

export const localhost = defineChain({
  id: 31337,
  name: 'Localhost',
  nativeCurrency: {
    decimals: 18,
    name: 'Ether',
    symbol: 'ETH',
  },
  rpcUrls: {
    default: { http: ['http://127.0.0.1:8545'] },
  },
  chainNamespace: 'eip155',
  caipNetworkId: 'eip155:31337',
})

// for custom networks visit -> https://docs.reown.com/appkit/react/core/custom-networks
export const networks = [localhost, baseSepolia] as [
  AppKitNetwork,
  ...AppKitNetwork[],
]

// Set up Solana Adapter
export const ethersAdapter = new EthersAdapter()
