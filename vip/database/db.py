import logging, asyncio, time, pytz, re, os, math, json, random, base64, sys, requests
from pyrogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo
from pyrogram import errors, filters, types, Client
from motor.motor_asyncio import AsyncIOMotorClient
from vip.info import *


client = AsyncIOMotorClient(DATABASE_URI)
mydb = client[DATABASE_NAME]

class Database:
    def __init__(self):
        self.col = mydb.users


    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)

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

    async def get_all_users(self):
        return self.col.find({})

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count


db = Database()
