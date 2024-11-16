

async def login():
    if os.path.exists(COOKIE_PATH) and os.path.getsize(COOKIE_PATH) > 0:
        client.load_cookies(COOKIE_PATH)
    elif COOKIES_JSON is not None and COOKIES_JSON != "":
        cookies = json.loads(COOKIES_JSON)
        client.set_cookies(cookies)
    else:
        await client.login(auth_info_1=EMAIL, auth_info_2=USERNAME, password=PASSWORD)
        client.save_cookies(COOKIE_PATH)
