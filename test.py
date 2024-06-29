from app.services.sms_receive import SmsReceive


async def test():
    sms = SmsReceive()
    print(await sms.get_balance())


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
    loop.close()
