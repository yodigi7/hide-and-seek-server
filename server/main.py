import asyncio
import traceback
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK, ConnectionClosed
from game import Game
from messages import (
    JoinGameRequest,
    UpdateMoveRequest,
    SuccessFailMessage,
    GridUpdateMessage,
    GameOverMessage,
    Role,
    Status,
)

seeker_found = False
hider_found = False
hider_connection = None
seeker_connection = None
game = None
background_game_loop = None


async def reset():
    global seeker_found, hider_found, hider_connection, seeker_connection
    if hider_connection:
        try:
            await hider_connection.close(1000)
        except Exception as e:
            print("Issue closing the hider connection", e)
    if seeker_connection:
        try:
            await seeker_connection.close(1000)
        except Exception as e:
            print("Issue closing the seeker connection", e)
    hider_connection = None
    seeker_connection = None
    seeker_found = False
    hider_found = False
    print("reset game")


async def update_hider(payload):
    global hider_connection
    try:
        await hider_connection.send(payload)
    except ConnectionClosed as e:
        print(e)
        hider_connection = None


async def update_seeker(payload):
    global seeker_connection
    try:
        await seeker_connection.send(payload)
    except ConnectionClosed as e:
        print(e)
        seeker_connection = None


async def game_loop():
    try:
        global game, background_game_loop
        game = Game()
        while hider_connection is not None and seeker_connection is not None:
            game.game_step()
            hider_board = game.get_board()
            seeker_board = game.get_board_seeker()
            if game.is_over():
                await asyncio.gather(
                    update_hider(GridUpdateMessage(grid=hider_board).model_dump_json()),
                    update_seeker(GridUpdateMessage(grid=seeker_board).model_dump_json()),
                )
                print(f"Game over in {game.current_game_step} steps")
                game_over_payload = GameOverMessage(
                    game_steps=game.current_game_step
                ).model_dump_json()
                await asyncio.gather(
                    update_hider(game_over_payload), update_seeker(game_over_payload)
                )
                break
            await asyncio.gather(
                asyncio.sleep(0.5),
                update_hider(GridUpdateMessage(grid=hider_board).model_dump_json()),
                update_seeker(GridUpdateMessage(grid=seeker_board).model_dump_json()),
            )
        await reset()
        background_game_loop = None
    except Exception as e:
        print("unexpected error")
        print(e)
        traceback.print_exc()
        await reset()
        raise e


async def handle_read(websocket):
    global seeker_found, hider_found, background_game_loop
    pos = await get_position(websocket)
    assert pos == Role.SEEKER or pos == Role.HIDER
    if seeker_found and hider_found:
        background_game_loop = asyncio.create_task(game_loop())
    async for message in websocket:
        move = UpdateMoveRequest.model_validate_json(message).move
        print(f"Got move: {move}")
        if pos == Role.SEEKER:
            if game.valid_seeker_move(move):
                game.seeker_move = move
                await websocket.send(
                    SuccessFailMessage(status=Status.SUCCESS).model_dump_json()
                )
            else:
                print("failed move")
                game.seeker_move = []
                await websocket.send(
                    SuccessFailMessage(status=Status.FAIL).model_dump_json()
                )
        elif pos == Role.HIDER:
            if game.valid_hider_move(move):
                game.hider_move = move
                print(f"successful hider move queue: {game.hider_move}")
                await websocket.send(
                    SuccessFailMessage(status=Status.SUCCESS).model_dump_json()
                )
            else:
                print("failed move")
                game.hider_move = []
                await websocket.send(
                    SuccessFailMessage(status=Status.FAIL).model_dump_json()
                )


async def get_position(websocket):
    global seeker_found, hider_found, seeker_connection, hider_connection
    async for message in websocket:
        if seeker_found and hider_found:
            await websocket.send("Full server, try again later.")
        role = JoinGameRequest.model_validate_json(message).role
        if role == Role.HIDER and hider_found:
            await websocket.send(SuccessFailMessage(status=Status.FAIL).model_dump_json())
            websocket.close(1000)
        elif role == Role.SEEKER and seeker_found:
            await websocket.send(SuccessFailMessage(status=Status.FAIL).model_dump_json())
            websocket.close(1000)
        elif role == Role.SEEKER:
            seeker_found = True
            seeker_connection = websocket
            await websocket.send(SuccessFailMessage(status=Status.SUCCESS).model_dump_json())
            print("found seeker")
            return Role.SEEKER
        else:
            hider_found = True
            hider_connection = websocket
            await websocket.send(SuccessFailMessage(status=Status.SUCCESS).model_dump_json())
            print("found hider")
            return Role.HIDER


async def handle_conn(websocket):
    try:
        await handle_read(websocket)
    except ConnectionClosedOK as e:
        print("Client closed connection", e)
    finally:
        await reset()


async def main():
    async with serve(handle_conn, "0.0.0.0", 8765) as server:
        print("Started server at port 8765")
        await server.serve_forever()


# Run the event loop
asyncio.run(main())
