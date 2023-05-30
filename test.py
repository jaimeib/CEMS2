import trio

# Global event object
event = trio.Event()


async def async_function():
    # Wait for the event to be set
    await event.wait()
    print("Async function started")


async def main():
    # Create the nursery for the async function
    async with trio.open_nursery() as nursery:
        # Start the async function
        nursery.start_soon(async_function)
        print("Main program started")
        # Sleep for a while
        await trio.sleep(2)
        # Set the event to signal the async function to continue
        event.set()


# Run the main function
trio.run(main)
