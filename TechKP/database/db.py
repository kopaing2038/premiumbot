import datetime
import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from TechKP.config.config import Config


client = AsyncIOMotorClient(Config.DATABASE_URI)
mydb = client[Config.SESSION_NAME]
fsubs = client['fsubs']


class Database:
    def __init__(self):
        self.col = mydb.user
        self.ucol = mydb.users
        self.grp = mydb.groups
        self.users = mydb.Premium_user

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            point = 0,
            ban_status=dict(
                is_banned=False,
                ban_reason=""
            )
        )

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)

    async def total_user_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_user(self):
        return self.col.find({})

    async def total_user_ucount(self):
        count = await self.ucol.count_documents({})
        return count

    async def get_uall_user(self):
        return self.ucol.find({})

    async def get_all_users(self):
        cursor = self.ucol.find({})
        users = await cursor.to_list(length=None)
        return users

    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason=""
            )
        )
    
    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)

    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})
        return False if not chat else chat.get('chat_status')  
    
    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    
    async def get_all_chats(self):
        return self.grp.find({})

    async def get_all_group(self):
        cursor = self.grp.find({})
        users = await cursor.to_list(length=None)
        return users

    async def delete_chat(self, id):
        await self.grp.delete_many({'id': int(id)})


    async def get_all_premium(self):
        return self.users.find({})

    async def get_premium_users(self):
        cursor = self.users.find({})
        users = await cursor.to_list(length=None)
        return users

    async def get_user(self, user_id):
        user_data = await self.users.find_one({"id": user_id})
        return user_data
            
    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

    async def premium_users_count(self):
        count = await self.users.count_documents({})
        return count

    async def has_premium_access(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            expiry_time = user_data.get("expiry_time")
            if expiry_time is None:
                # User previously used the free trial, but it has ended.
                return False
            elif isinstance(expiry_time, datetime.datetime) and datetime.datetime.now() <= expiry_time:
                return True
            else:
                await self.users.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
        return False

    async def check_remaining_uasge(self, userid):
        user_id = userid
        user_data = await self.get_user(user_id)        
        expiry_time = user_data.get("expiry_time")
        # Calculate remaining time
        remaining_time = expiry_time - datetime.datetime.now()
        return remaining_time


    async def all_premium_users(self):
        count = await self.users.count_documents({
        "expiry_time": {"$gt": datetime.datetime.now()}
        })
        return count


db = Database()
