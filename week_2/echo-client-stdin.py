# echo-client.py

import sys
import trio

# arbitrary, but:
# - must be in between 1024 and 65535
# - can't be in use by some other program on your computer
# - must match what we set in our echo server
PORT = 12345

async def sender(client_stream):
    print("sender: started!")
    file_stream =  await trio.open_file("/dev/stdin", mode="rb")
    async with file_stream as my_file:
        while True:
            async for line in my_file:
                print("sender: sending {!r}".format(line))
                await client_stream.send_all(line)
                await trio.sleep(1)


async def receiver(client_stream):
    print("receiver: started!")
    async for data in client_stream:
        print("receiver: got data {!r}".format(data))
    print("receiver: connection closed")
    sys.exit()

async def parent():
    print("parent: connecting to 127.0.0.1:{}".format(PORT))
    client_stream = await trio.open_tcp_stream("127.0.0.1", PORT)
    async with client_stream:
        async with trio.open_nursery() as nursery:
            print("parent: spawning sender...")
            nursery.start_soon(sender, client_stream)

            print("parent: spawning receiver...")
            nursery.start_soon(receiver, client_stream)

trio.run(parent)
