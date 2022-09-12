import random
import json
from pathlib import Path
from typing import List, Dict, Union, Tuple, Any, Optional
from PIL import Image
from io import BytesIO
from core import BytesIOToBytes
import httpx

tarot_path = Path(__file__).absolute().parent / "resource"


class Tarot:
    _init: bool = False
    _formations: Dict[str, Dict[str, Union[int, bool, List[List[str]]]]] = {}
    _cards: Dict[str, Dict[str, Union[str, Dict[str, str]]]] = {}
    is_chain_reply: bool = True
    divined: List[str] = []
    is_cut: bool = False
    represent: List[str] = []

    def __init__(self):
        self.formation_name = random.choice(list(self._formations))
        self.formation = self._formations.get(self.formation_name)

        self.cards_num: int = 0
        self.cards_num = self.formation.get("cards_num")
        self.divined = random.sample(list(self._cards), self.cards_num)
        self.is_cut = self.formation.get("is_cut")
        self.represent = random.choice(self.formation.get("represent"))

    async def reveal(self, index: int) -> Tuple[str, bytes]:
        if self.is_cut and index == self.cards_num - 1:
            msg_header = f"切牌「{self.represent[index]}」\n"
        else:
            msg_header = f"第{index + 1}张牌「{self.represent[index]}」\n"

        msg_body, img = await self.multi_divine(index)

        return msg_header + msg_body, img

    async def multi_divine(self, index: int) -> Tuple[str, Optional[bytes]]:
        card: Dict[str, Any] = self._cards.get(self.divined[index])
        return await self.single_divine(card)

    @staticmethod
    async def single_divine(card: Dict[str, Any]) -> Tuple[str, Optional[bytes]]:
        name_cn: str = card.get("name_cn")
        img_path: Path = tarot_path / card.get("type") / card.get("pic")

        if not img_path.exists():
            res = httpx.get(
                f"https://raw.fastgit.org/MinatoAquaCrews/nonebot_plugin_tarot/beta/nonebot_plugin_tarot/resource/{card.get('type')}/{card.get('pic')}")
            if res is None:
                return f"图片下载出错，请重试……", None
            img_path.parent.mkdir(exist_ok=True)
            with open(str(img_path), "wb") as f:
                f.write(res.content)

        img = Image.open(img_path)

        if random.random() < 0.5:
            # 正位
            meaning = card.get("meaning").get("up")
            msg = f"「{name_cn}正位」「{meaning}」\n"
        else:
            meaning = card.get("meaning").get("down")
            msg = f"「{name_cn}逆位」「{meaning}」\n"
            img = img.rotate(180)

        buf = BytesIO()
        img.save(buf, format='png')

        return msg, BytesIOToBytes(buf)

    @classmethod
    def init_json(cls):
        tarot_json: Path = tarot_path / "tarot.json"
        with open(str(tarot_json), 'r', encoding='utf-8') as f:
            content = json.load(f)
            cls._formations = content.get("formation")
            cls._cards = content.get("cards")
        cls._init = True

    @classmethod
    async def divine(cls):
        if not cls._init:
            cls.init_json()

        obj = cls()
        yield {"message": f"启用{obj.formation_name}，正在洗牌中", "image": None}

        for i in range(obj.cards_num):
            msg, img = await obj.reveal(i)
            yield {"message": msg, "image": img}

    @classmethod
    async def tarot(cls):
        if not cls._init:
            cls.init_json()

        msg, img = await cls.single_divine(random.choice(list(cls._cards.values())))

        return {"message": "回应是" + msg, "image": img}
