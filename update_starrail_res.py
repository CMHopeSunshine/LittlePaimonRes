import asyncio
import os
# import zipfile
from pathlib import Path

import httpx
from pydantic import BaseModel
from tqdm import tqdm

star_rail_res_path = Path(__file__).parent / "LittlePaimon" / "star_rail"
this_path = str(Path().absolute())
remote_api = "https://api.github.com/repos/Mar-7th/StarRailRes/contents/{}"
self_api = "https://api.github.com/repos/CMHopeSunshine/LittlePaimonRes/contents/LittlePaimon/star_rail/{}"

res_prefix = ["image/", "icon/", "icon/", "icon/"]
remote_res_list = ["character_portrait", "light_cone", "relic", "skill"]

token = os.environ["GITHUB_TOKEN"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {token}",
}


class Content(BaseModel):
    name: str
    sha: str
    download_url: str


async def get_remote_res_list():
    res_list = []
    async with httpx.AsyncClient(headers=headers) as client:
        remote_res_tasks = [
            client.get(remote_api.format(res_prefix[i] + remote_res_list[i]))
            for i in range(4)
        ]
        self_res_tasks = [
            client.get(self_api.format(remote_res_list[i])) for i in range(4)
        ]
        remote_res_results = await asyncio.gather(*remote_res_tasks)
        self_res_results = await asyncio.gather(*self_res_tasks)
        for i in range(4):
            remote_res = [
                Content.model_validate(item) for item in remote_res_results[i].json()
            ]
            self_res = [
                Content.model_validate(item) for item in self_res_results[i].json()
            ]
            self_res_dict = {item.name: item for item in self_res}
            for item in remote_res:
                if item.name not in self_res_dict:
                    res_list.append(item.download_url)
                elif item.sha != self_res_dict[item.name].sha:
                    res_list.append(item.download_url)
    return res_list


async def download_res():
    res_list = await get_remote_res_list()
    semaphore = asyncio.Semaphore(4)
    total_tasks = len(res_list)

    async with httpx.AsyncClient(headers=headers) as client:
        with tqdm(total=total_tasks, desc="Downloading") as pbar:
            download_tasks = [
                asyncio.create_task(limited_download(client, url, semaphore, pbar))
                for url in res_list
            ]
            await asyncio.gather(*download_tasks)


async def limited_download(client, url, semaphore, pbar):
    async with semaphore:
        response = await client.get(url)
        res_path = star_rail_res_path
        file_path = (
            res_path
            / response.url.path.split("/")[-2]
            / response.url.path.split("/")[-1]
        )
        with open(file_path, "wb") as f:
            f.write(response.content)
        pbar.update(1)


if __name__ == "__main__":
    asyncio.run(download_res())
    # path = this_path + "/star_rail.zip"
    # with zipfile.ZipFile(path, "w") as zf:
    #     for file in star_rail_res_path.rglob("*"):
    #         zf.write(file, file.relative_to(star_rail_res_path))
    print("StarRailRes updated.")
