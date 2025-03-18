import React, { useState, useEffect } from 'react'
import Board from './Board'

import { Message, BatchState, MessageType } from './websocket'

import { createAppKit } from '@reown/appkit/react'
import { networks, projectId, metadata, ethersAdapter } from './config'

import { useAppKitAccount, useAppKitProvider } from '@reown/appkit/react'
import { BrowserProvider, Contract } from 'ethers'
import ABI from './abi.json'

const contractAddress = import.meta.env.VITE_APP_ADDRESS
const NULL_ADDRESS = '0x0000000000000000000000000000000000000000'
var contract: any = null
var ethersProvider: BrowserProvider
var signer: any

const BOARD_GRID_SIZE = 18

createAppKit({
  debug: true,
  adapters: [ethersAdapter],
  networks,
  metadata,
  projectId,
  features: {
    analytics: true, // Optional - defaults to your Cloud configuration
  },
})

enum Color {
  Black = 'BLACK',
  White = 'WHITE',
}

enum RequestType {
  New = 'NEW',
  Proceed = 'PROCEED',
}

const toggleColorMap: { [key in Color]: Color } = {
  [Color.Black]: Color.White,
  [Color.White]: Color.Black,
}

enum PlayerStatus {
  Unconnected,
  Unjoined,
  Pairing,
  Gaming,
  Finished,
  Settled,
}

const App: React.FC = () => {
  // game states
  const [step, setStep] = useState(0)
  const [playerColor, setPlayerColor] = useState<{ [key: string]: string }>({})
  const [nextColor, setNextColor] = useState<Color>(Color.Black)
  const [squares, setSquares] = useState<Array<string | null>>(
    Array((BOARD_GRID_SIZE + 1) * (BOARD_GRID_SIZE + 1)).fill(null)
  )

  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [winner, setWinner] = useState<string | null>(null)
  const [playerStatus, setPlayerStatus] = useState(PlayerStatus.Unconnected)

  // abci server state
  const [roomId, setRoomId] = useState<string | null>(null)

  // onchain states
  const [onChainRoomId, setOnChainRoomId] = useState<number | null>(null)
  const [onChainWinner, setOnChainWinner] = useState<number | null>(null)

  // wallet connection
  const { address } = useAppKitAccount()
  const { walletProvider } = useAppKitProvider('eip155')

  const initContract = async () => {
    if (!walletProvider) {
      console.log('Wallet not connected')
      return
    }

    if (contract != null) {
      return
    }

    ethersProvider = new BrowserProvider(walletProvider as any)
    signer = await ethersProvider.getSigner()
    contract = new Contract(contractAddress, ABI, signer)
  }

  useEffect(() => {
    if (address == null) {
      return
    }
    // address connected
    if (playerStatus === PlayerStatus.Unconnected) {
      setPlayerStatus(PlayerStatus.Unjoined)
      return
    }

    if (playerStatus === PlayerStatus.Unjoined) {
      const checkRoom = async () => {
        const roomId = await getPlayerRoomId()
        if (roomId != 0) {
          setOnChainRoomId(roomId)
          setPlayerStatus(PlayerStatus.Pairing)
        }
      }
      checkRoom()
      return
    }

    // start check on chain session before start
    if (playerStatus === PlayerStatus.Pairing) {
      const intervalId = setInterval(async () => {
        try {
          if (onChainRoomId == null) {
            const roomId = await getPlayerRoomId()
            setOnChainRoomId(roomId)
          }

          const session = await getSession()

          if (session.status == 2) {
            clearInterval(intervalId)
            await loginServer(session.endpoint)
            setPlayerStatus(PlayerStatus.Gaming)
          }
        } catch (error) {
          console.error('Error polling session:', error)
        }
      }, 2000)
      return () => clearInterval(intervalId)
    }

    // check if settled
    if (playerStatus === PlayerStatus.Finished) {
      const intervalId = setInterval(async () => {
        try {
          console.log(`roomId `, onChainRoomId)
          const room = await getRoomById(onChainRoomId!)
          if (room.winner !== NULL_ADDRESS) {
            clearInterval(intervalId)
            console.log('settlement', room.winner)
            setOnChainWinner(room.winner)
            setPlayerStatus(PlayerStatus.Settled)
          }
        } catch (error) {
          console.error('Error polling room:', error)
        }
      }, 2000)
      return () => clearInterval(intervalId)
    }
  }, [address, playerStatus, onChainRoomId])

  // TO be used for signing
  function randomString(length: number) {
    const chars =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let result = ''
    const charactersLength = chars.length
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * charactersLength))
    }
    return result
  }

  // On Chain Operations:
  async function joinGame() {
    await initContract()

    const tx = await contract.joinOrCreateRoom()
    console.log('Transaction joinOrCreateRoom:', tx)

    const receipt = await tx.wait()
    console.log('Join room', receipt)

    // TODO: check if user already in a room
    if (receipt.status == 1) {
      console.log('Joined successfully', receipt.status)
      return true
    } else {
      console.log('Failed to join', receipt)
      return false
    }
  }

  async function getPlayerRoomId() {
    await initContract()
    console.log('signer', signer.address)
    const playerRoomId = await contract.getPlayerRoom(address)
    console.log('playerRoom', playerRoomId, playerRoomId != 0)
    return playerRoomId
  }

  async function getRoomById(roomId: number) {
    await initContract()

    const room = await contract.getRoom(roomId)
    console.log('room', room)
    return room
  }

  async function getSession() {
    await initContract()

    const session = await contract.getSession()
    console.log('session', session)
    return session
  }

  async function sign(message: string) {
    await initContract()
    const signer = await ethersProvider.getSigner()
    return signer.signMessage(message)
  }

  async function loginServer(endpoint: string) {
    try { 
      // sign the message
      const message = 'LOGIN-GOMOKU-' + randomString(16)
      const signature = await sign(message)

      console.log(message, signature)

      const response = await fetch("http://"+endpoint + '/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          address: address,
          message: message,
          signature: signature,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Server response:', data)
      connectServer(endpoint)
    } catch (error) {
      console.error('Error connecting to server:', error)
    }
  }

  async function connectServer(endpoint: string) {
    initWebsocket(endpoint)
    console.log('init ok')
  }

  const initWebsocket = (endpoint: string) => {
    let newSocket: WebSocket 
    const addr = address as string

    const connectWebSocket = () => {
      newSocket = new WebSocket(`ws://${endpoint}/ws`)

      newSocket.onopen = () => {
        console.log('WebSocket connect successed') 
        const content = {
          requestType: RequestType.New,
          address: address,
          position: null,
        }
        const data = new TextEncoder().encode(JSON.stringify(content))
        const message = {
          type: MessageType.REQUEST,
          address: address,
          timestamp: Date.now(),
          data: data,
          signature: new Uint8Array(),
        }
        const wsMsg = Message.encode(message).finish()
        newSocket.send(wsMsg)
      }

      newSocket.onmessage = (event) => {
        event.data.arrayBuffer().then((buffer: any) => {
          const message = Message.decode(new Uint8Array(buffer))
          if (message.type === MessageType.RESPONSE) {
            const responseArr = BatchState.decode(message.data)
            responseArr.states.forEach((x) => {
              if (x.attributes[0].key == 'data') {
                return
              }
              const serverRoom = JSON.parse(x.attributes[0].value)
              console.log('Parsed serverRoom:', serverRoom)

              if (!serverRoom || Object.keys(serverRoom).length === 0) {
                console.log('Early return: serverRoom is empty or null')
                return
              }
              if (roomId && roomId !== serverRoom.roomId) {
                console.log('Early return: roomId mismatch', {
                  roomId,
                  serverRoomRoomId: serverRoom.roomId,
                })
                return
              }
              if (serverRoom.state.playerColor[addr] == null) {
                console.log(
                  'Early return: playerColor is null for address',
                  address
                )
                return
              }

              if (serverRoom?.playerColor?.length < 2) {
                // waiting for both user to be ready
                return;
              }

              console.log('color', serverRoom.state.playerColor[addr])

              const state = serverRoom.state
              if (step > 0 && state.step <= step) {
                console.log('Early return: step is not greater', {
                  step,
                  stateStep: state.step,
                })
                return
              }

              setRoomId(roomId || serverRoom.roomId)
              setStep(state.step)
              setPlayerColor(state.playerColor)
              setNextColor(state.nextColor)
              setSquares(state.squares)
              setWinner(state.winner)

              if (state.winner != null) {
                setPlayerStatus(PlayerStatus.Finished)
              }
              console.log('set all')
            })
          }
        })
      }

      newSocket.onerror = (error) => {
        console.error('WebSocket connect error:', error)
        newSocket.close()
      }

      newSocket.onclose = (event) => {
        console.log('WebSocket connection closed:', event)
        // TODO: retry reconnect
      }

      setSocket(newSocket)
    }

    connectWebSocket()
  }

  const handleClick = (i: number) => {
    console.log('Clicking: ', i)
    if (squares[i]) {
      console.log('Early return: square is already occupied', {
        index: i,
        squareValue: squares[i],
      })
      return
    }

    if (winner) {
      console.log('Early return: game already has a winner', { winner })
      return
    }

    if (nextColor !== playerColor[address]) {
      console.log("Early return: not the player's turn", {
        nextColor,
        playerColor: playerColor[address],
      })
      return
    }

    // update local first then update remote
    // update local
    const position = i
    squares[position] = nextColor
    setSquares(squares)
    setNextColor(toggleColorMap[nextColor])
    setStep(step + 1)

    const winnerColor = winnerColorIs(squares)
    if (winnerColor) {
      const winnerAddress = Object.entries(playerColor).find(
        ([key, value]) => value === winnerColor
      )?.[0]

      setWinner(winnerAddress as any)
    }

    // update remote
    const content = {
      requestType: RequestType.Proceed,
      address,
      position,
    }
    const data = new TextEncoder().encode(JSON.stringify(content))
    const message = {
      type: 0,
      address,
      timestamp: Date.now(),
      data: data,
      signature: new Uint8Array(),
    }
    const wsMsg = Message.encode(message).finish()
    socket?.send(wsMsg)
  }

  const block = Array(BOARD_GRID_SIZE * BOARD_GRID_SIZE).fill(null)

  const handleJoinClick = async () => {
    // TODO: handle failure
    const res = await joinGame()

    if (res) {
      setPlayerStatus(PlayerStatus.Pairing)
    }
  }

  const handleRestartClick = async () => {
    await handleJoinClick()
    // TODO: tmp sln for all state reset
    window.location.reload()
  }

  // status:
  // 1. connect to your wallet
  // 2. join game
  // 3. Matching in progress..
  // 4. your turn / waiting for the opponent
  // 5. you win/lose. Result settling on chain for winner (address)

  const actionAreaData = () => {
    let text = ''
    let action = <appkit-button />
    if (playerStatus === PlayerStatus.Unconnected) {
      text = 'Connect your wallet'
    } else if (playerStatus === PlayerStatus.Unjoined) {
      text = 'Join the game'
      action = (
        <button className="game__button" onClick={handleJoinClick}>
          Join Game
        </button>
      )
    } else if (playerStatus === PlayerStatus.Pairing) {
      text = 'Matching in progress..'
    } else if (playerStatus === PlayerStatus.Gaming) {
      text =
        nextColor === playerColor[address as string]
          ? `${nextColor} (you) to move`
          : 'Waiting for the opponent'
    } else if (playerStatus === PlayerStatus.Finished) {
      let res = 'You'
      if (winner === address) {
        res += ' win!'
      } else {
        res += ' lose.'
      }

      res += ' Result settling..'
      text = res
    } else if (playerStatus === PlayerStatus.Settled) {
      text = `Winner (${onChainWinner}) settled on chain.`

      action = (
        <button className="game__button" onClick={handleRestartClick}>
          New Game
        </button>
      )
    }

    return { text, action }
  }

  return (
    <div className="container">
      <div className="game">
        <div className="game__title">
          <h2>Gomoku Game</h2>
        </div>
        <div className="game__field">
          <div className="game__board__bg">
            {block.map((item, index) => (
              <div className="block" key={index}>
                {item}
              </div>
            ))}
          </div>
          <Board squares={squares} handleClick={handleClick} />
        </div>
        <div className="game__info">
          <div className="game__status">{actionAreaData().text}</div>
          <div className="game__button__container">
            {actionAreaData().action}
          </div>
        </div>
      </div>
    </div>
  )
}

function winnerColorIs(squares: any) {
  // Define 12 possible winning lines in a 5x5 grid
  const lines = [
    [0, 1, 2, 3, 4],
    [19, 20, 21, 22, 23],
    [38, 39, 40, 41, 42],
    [57, 58, 59, 60, 61],
    [76, 77, 78, 79, 80],
    [0, 19, 38, 57, 76],
    [1, 20, 39, 58, 77],
    [2, 21, 40, 59, 78],
    [3, 22, 41, 60, 79],
    [4, 23, 42, 61, 80],
    [0, 20, 40, 60, 80],
    [4, 22, 40, 58, 76],
  ]

  for (let i = 0; i <= 14; i++) {
    // 5x5 board horizontal scan
    for (let j = 0; j <= 14; j++) {
      // 5x5 board vertical scan
      const newlines = lines.map((line) => {
        const newline = line.map((num) => num + i * 19 + j)
        return newline
      })

      for (let k = 0; k < newlines.length; k++) {
        // Scan 12 possible winning lines
        const [a, b, c, d, e] = newlines[k]
        if (
          squares[a] &&
          squares[a] === squares[b] &&
          squares[a] === squares[c] &&
          squares[a] === squares[d] &&
          squares[a] === squares[e]
        ) {
          return squares[a]
        }
      }
    }
  }
  return null
}
export default App
