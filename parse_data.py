def parse_http_proxies_from_file(path: str) -> list[str]:
    """

    :rtype: object
    """
    proxies_list = [line.replace("\n", "").strip() for line in open(path)]

    for index, line in enumerate(proxies_list):
        if line != "":
            http_url, http_port, username, password = line.split(":")
            proxy = f"http://{username}:{password}@{http_url}:{http_port}"
            proxies_list[index] = proxy

    return proxies_list


def parse_tokens_from_file(path: str) -> list[str]:
    return [line.replace("\n", "").strip().split(":")[0] for line in open(path)]
