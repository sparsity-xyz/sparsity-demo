import React from 'react'

enum Color {
  Black = 'BLACK',
  White = 'WHITE',
}

function Square(props: any) {
  const { index, value, handleClick } = props
  return (
    <div
      className="square"
      onClick={() => {
        handleClick(index)
      }}
    >
      {value && (
        <div className={value === Color.Black ? 'black' : 'white'}></div>
      )}
    </div>
  )
}

// 19*19 board
interface BoardProps {
  squares: (string | null)[]
  handleClick: (index: number) => void
}

function Board(props: BoardProps) {
  const { squares, handleClick } = props
  return (
    <div className="game__board">
      {squares.map((item, index) => (
        <Square
          key={index}
          index={index}
          value={item}
          handleClick={handleClick}
        />
      ))}
    </div>
  )
}

export default Board
