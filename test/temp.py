import asyncio


async def main():
    print('loop in main(): ', asyncio.get_event_loop())


if __name__ == '__main__':
    print('loop in __main__: ', asyncio.get_event_loop())
    asyncio.run(main())
