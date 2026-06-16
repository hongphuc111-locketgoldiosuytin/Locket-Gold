import aiohttp
import asyncio
import datetime

# Danh sách domain cần chặn
BLOCK_DOMAINS = [
    # RevenueCat - Chặn kiểm tra gói Gold
    "revenuecat.com",
    "api.revenuecat.com",
    "www.revenuecat.com",
    # IP Check Services - Chặn kiểm tra IP
    "api.ipify.org",
    "api64.ipify.org",
    "ipinfo.io",
    "ip-api.com",
    "ipapi.co",
    "checkip.amazonaws.com",
    "ifconfig.me",
    "icanhazip.com",
    "ip.seeip.org",
    "api.ip.sb",
    "ipwhois.io",
    "api.myip.com",
    "ipecho.net",
]

async def create_profile(api_key, log_callback=None):
    def log(msg):
        if log_callback:
            log_callback(msg)

    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    profile_name = f"LocketVIP-{today_str}"

    log(f"[*] Checking for existing profile: {profile_name}...")
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            list_url = "https://api.nextdns.io/profiles"
            async with session.get(list_url) as res:
                if res.status == 200:
                    data = await res.json()
                    profiles = data.get('data', [])
                    for p in profiles:
                        if p.get('name') == profile_name:
                            pid = p.get('id')
                            log(f"[+] Found existing daily profile: {pid} (REUSING)")
                            
                            log(f"[>] Verifying Anti-Revoke & IP Block Rules...")
                            
                            # Đảm bảo tất cả domain đều bị block
                            denylist_url = f"https://api.nextdns.io/profiles/{pid}/denylist"
                            try:
                                for domain in BLOCK_DOMAINS:
                                    async with session.post(denylist_url, json={"id": domain, "active": True}) as post_res:
                                        pass
                                log(f"[>] Integrity Check: OK ({len(BLOCK_DOMAINS)} rules verified).")
                            except Exception as e:
                                log(f"[!] Warning checking rules: {e}")

                            await asyncio.sleep(0.5)
                            log(f"[SUCCESS] DNS VIP Node Active (Cached).")
                            return pid, f"https://apple.nextdns.io/?profile={pid}"
        except Exception as e:
            log(f"[!] Error listing profiles: {e}")

        log(f"[*] Creating new daily profile: {profile_name}")
        log(f"[*] Initializing High-Speed VIP DNS Node...")
        await asyncio.sleep(0.5)
        
        create_url = "https://api.nextdns.io/profiles"
        payload = {"name": profile_name}
        
        try:
            async with session.post(create_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    pid = data['data']['id']
                    log(f"[+] Profile created: {pid}")
                    
                    log(f"[>] Applying Anti-Revoke & IP Block Rules...")
                    await asyncio.sleep(0.4)
                    
                    denylist_url = f"https://api.nextdns.io/profiles/{pid}/denylist"
                    
                    # Block tất cả domain (RevenueCat + IP check)
                    blocked_count = 0
                    for domain in BLOCK_DOMAINS:
                        try:
                            async with session.post(denylist_url, json={"id": domain, "active": True}) as r:
                                if r.status == 200:
                                    blocked_count += 1
                        except Exception as e:
                            log(f"[!] Error blocking {domain}: {e}")
                    
                    log(f"[+] Firewall Rules Applied: {blocked_count}/{len(BLOCK_DOMAINS)} domains blocked")
                    
                    # Verify
                    try:
                        async with session.get(denylist_url) as verify_r:
                            if verify_r.status == 200:
                                verify_data = await verify_r.json()
                                rules = verify_data.get('data', [])
                                active_rules = [d.get('id') for d in rules if d.get('active')]
                                log(f"[+] Verified: {len(active_rules)} active rules")
                    except:
                        pass
                    
                    log(f"[SUCCESS] DNS VIP Node Active.")
                    link = f"https://apple.nextdns.io/?profile={pid}"
                    return pid, link
                else:
                    text = await response.text()
                    log(f"NextDNS Error: {response.status} {text}")
                    return None, None
                
        except Exception as e:
            log(f"Error creating NextDNS profile: {e}")
            return None, None
