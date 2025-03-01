import { ethers } from 'ethers'

import { startServer, BaseApplication, StepEvent } from '@sparsity/abci'

const BOARD_GRID_SIZE = 18

type Address = string

enum RequestType {
  New = 'NEW',
  Proceed = 'PROCEED',
}

enum Color {
  Black = 'BLACK',
  White = 'WHITE',
}

interface State {
  step: number
  playerColor: { [key: Address]: Color } // cannot use Map due to JSON serilization
  nextColor: Color
  // history: [ ],
  squares: Array<Color | null>
  winner: Address | null
  ready: boolean
}

// for now only one room per er
interface Room {
  state: State
  roomId: string
}

interface Message {
  address: Address
  requestType: RequestType
  position?: number
}

const toggleColorMap: { [key in Color]: Color } = {
  [Color.Black]: Color.White,
  [Color.White]: Color.Black,
}

function generateUniqueId() {
  return Math.random().toString(36).substring(2, 15)
}

function winnerColorIs(squares: any) {
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
    for (let j = 0; j <= 14; j++) {
      const newlines = lines.map((line) => {
        const newline = line.map((num) => num + i * 19 + j)
        return newline
      })

      for (let k = 0; k < newlines.length; k++) {
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

// my app logic
export class Application extends BaseApplication {
  // client to room number mapping
  private clientRooms: Map<Address, Room>
  private room: Room
  private endblockHeight: number

  constructor() {
    super()
    this.endblockHeight = 1000000

    this.clientRooms = new Map<Address, Room>()
    this.room = {
      roomId: generateUniqueId(),
      state: {
        step: 0, // Initialize step
        playerColor: {}, // Initialize color map
        nextColor: Color.Black, // Set initial next color
        squares: Array((BOARD_GRID_SIZE + 1) * (BOARD_GRID_SIZE + 1)).fill(
          null
        ), // Initialize squares for a 5x5 board
        winner: null, // Initialize winner
        ready: false, // Initialize ready state
      },
    }
  }

  // should executed only once
  init(initial: string) {}

  step(messages: Array<Message>): Array<StepEvent> {
    var events: Array<StepEvent> = []
    messages.forEach((msg) => {
      console.log('receiving message', msg)
      // validate
      const { address, position, requestType } = msg
      if (requestType === RequestType.Proceed && position == null) {
        console.log(`Invalid proceed message: `, msg)
        return
      }

      // update server state
      if (requestType === RequestType.New) {
        let lastRoom = this.room
        if (Object.keys(lastRoom.state.playerColor).length === 2) {
          const newRoom = {
            roomId: generateUniqueId(),
            state: {
              step: 0, // Initialize step
              playerColor: {}, // Initialize color map
              nextColor: Color.Black, // Set initial next color
              squares: Array(25).fill(null), // Initialize squares for a 5x5 board
              winner: null, // Initialize winner
              ready: false, // Initialize ready state
            },
          }
          this.room = newRoom
          lastRoom = newRoom
        }

        // avoid two players in one room to be same
        if (this.clientRooms.get(address) === lastRoom) {
          return
        }

        this.clientRooms.set(address, lastRoom)

        lastRoom.state.playerColor[address] =
          Object.keys(lastRoom.state.playerColor).length === 0
            ? Color.Black
            : Color.White

        if (Object.keys(lastRoom.state.playerColor).length === 2) {
          lastRoom.state.ready = true
          lastRoom.state.nextColor = Color.Black
        }
      } else if (requestType === RequestType.Proceed) {
        // find room
        const clientRoom = this.clientRooms.get(address)
        if (clientRoom == null) {
          console.log(`No room found: `, msg)
          return
        }

        const roomState = clientRoom.state

        if (roomState.nextColor !== roomState.playerColor[address]) {
          console.log(`Not the player's turn: `, msg)
          return
        }

        if (position == null) {
          console.log(`Missing position: `, msg)
          return
        }

        roomState.step++
        roomState.squares[position] = roomState.nextColor
        roomState.nextColor = toggleColorMap[roomState.nextColor]
        const winnerColor = winnerColorIs(roomState.squares)
        if (winnerColor) {
          const winnerAddress = Object.entries(roomState.playerColor).find(
            ([key, value]) => value === winnerColor
          )?.[0]
          if (winnerAddress) {
            roomState.winner = winnerAddress
          }
        }
      } else {
        console.log(`Invalid request type: `, msg)
      }

      // send response
      const roomInfo = this.clientRooms.get(address)

      console.log('roomInfo', roomInfo)

      events.push({
        type: '__room__',
        key: msg.address,
        value: JSON.stringify(roomInfo),
      })

      // TODO: remove room from server memory if winner exits
    })
    return events
  }

  status(): [isEnd: boolean, data: string] {
    if (this.room.state.winner != null) {
      console.log(`status: `, true, this.resultData())
      return [true, this.resultData()]
    }
    return [false, '']
  }

  resultData() {
    const state = this.room.state

    const black = Object.keys(state.playerColor)[0]
    const white = Object.keys(state.playerColor)[1]
    const winner = state.winner

    const data = ethers.AbiCoder.defaultAbiCoder().encode(
      ['address', 'address', 'address'],
      [black, white, winner]
    )
    return data
  }
}

startServer(new Application())
