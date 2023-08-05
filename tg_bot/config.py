from dataclasses import dataclass
from typing import List

from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: List[int]
    use_redis: bool
    
@dataclass
class DBConfig:
    HOST: str
    PASSWORD: str
    USER: str
    NAME: str
    POSTGRES_URI: str
    
@dataclass
class Miscellaneous:
    PAYMENT_TOKEN: str
    other_params: str = None

@dataclass
class Config:
    tg_bot: TgBot
    db: DBConfig
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)
    
    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS")
        ),
        
        db=DBConfig(
            HOST=env.str("DB_HOST"),
            PASSWORD=env.str("DB_PASSWORD"),
            USER=env.str("DB_USER"),
            NAME=env.str("DB_NAME"),
            POSTGRES_URI='postgresql://sapphire:doos16xot@localhost/sibsutis_db'
            # POSTGRES_URI=f'postgresql://{env.str("DB_USER")}:{env.str("DB_PASSWORD")}@{env.str("DB_HOST")}/{env.str("DB_NAME")}'
        ),
        misc=Miscellaneous(
            PAYMENT_TOKEN=env.str("PAYMENT_TOKEN")
        )
    )
