import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from telethon.tl import functions
from telethon.tl.types import InputMessagesFilterDocument
from userbot import CMD_HELP, AUTO_PP, ASYNC_POOL
from userbot.events import register
import asyncio
import random
import shutil
import requests
import time
from telethon.errors import VideoFileInvalidError


from userbot.language import get_value
LANG = get_value("autopp")


@register(outgoing=True, pattern="^.autovideo ?(.*)$")
async def autovideo(event):
    if 'autovideo' in ASYNC_POOL:
        await event.edit(LANG['VIDEO_ALREADY_CHANGING'])
        return

    if not event.reply_to_msg_id:
        return await event.edit(LANG['NEED_VIDEO'])
    else:
        await event.edit(LANG['SETTING_VIDEO'])
        
        reply = await event.get_reply_message()
        video = await reply.download_media()
        yazi = event.pattern_match.group(1)

    try:
        os.remove("./pp.mp4")
    except:
        pass

    try:
        await event.client(functions.photos.UploadProfilePhotoRequest(
            video=await event.client.upload_file(video)
        ))
    except VideoFileInvalidError:
        return await event.edit(LANG['INVALID_VIDEO'])
    
    ASYNC_POOL.append('autovideo')

    await event.edit(LANG['STARTED_VIDEO'])
    while "autovideo" in ASYNC_POOL:
        saat = time.strftime("%H\.%M")
        tarih = time.strftime("%d\/%m\/%Y")

        if yazi:
            yazi = yazi.replace("$saat", saat).replace("$tarih", tarih)
            KOMUT = f"text=\'{yazi}\' :expansion=normal: y=h-line_h-10:x=(mod(5*n\,w+tw)-tw): fontcolor=white: fontsize=30: box=1: boxcolor=black@0.5: boxborderw=5: shadowx=2: shadowy=2"
        else:
            KOMUT = f"text=\'Saat\: {saat} Tarih\: {tarih} {yazi}\' :expansion=normal: y=h-line_h-10:x=(mod(5*n\,w+tw)-tw): fontcolor=white: fontsize=30: box=1: boxcolor=black@0.5: boxborderw=5: shadowx=2: shadowy=2"

        ses = await asyncio.create_subprocess_shell(f"ffmpeg -y -i '{video}' -vf drawtext=\"{KOMUT}\" pp.mp4")
        await ses.communicate()

        await event.client(functions.photos.UploadProfilePhotoRequest(
            video=await event.client.upload_file("pp.mp4")
        ))
        os.remove("./pp.mp4")
        await asyncio.sleep(60)

    os.remove(video)

@register(outgoing=True, pattern="^.autopp (.*)")
async def autopic(event):
    if 'autopic' in ASYNC_POOL:
        await event.edit(LANG['PHOTO_ALREADY_CHANGING'])
        return

    await event.edit(LANG['SETTING'])

    FONT_FILE_TO_USE = await get_font_file(event.client, "@FontDunyasi")

    downloaded_file_name = "./userbot/eskipp.png"
    r = requests.get(AUTO_PP)

    with open(downloaded_file_name, 'wb') as f:
        f.write(r.content)    
    photo = "yenipp.png"
    await event.edit(LANG['SETTED'])

    ASYNC_POOL.append('autopic')

    while 'autopic' in ASYNC_POOL:
        shutil.copy(downloaded_file_name, photo)
        current_time = datetime.now().strftime("%H:%M")
        img = Image.open(photo)
        drawn_text = ImageDraw.Draw(img)
        fnt = ImageFont.truetype(FONT_FILE_TO_USE, 70)
        size = drawn_text.multiline_textsize(current_time, font=fnt)
        drawn_text.text(((img.width - size[0]) / 2, (img.height - size[1])),
                       current_time, font=fnt, fill=(255, 255, 255))
        img.save(photo)
        file = await event.client.upload_file(photo)  # pylint:disable=E0602
        try:
            await event.client(functions.photos.UploadProfilePhotoRequest(  # pylint:disable=E0602
                file
            ))
            os.remove(photo)
            await asyncio.sleep(60)
        except:
            return

async def get_font_file(client, channel_id):
    # Önce yazı tipi mesajlarını al
    font_file_message_s = await client.get_messages(
        entity=channel_id,
        filter=InputMessagesFilterDocument,
        limit=None
    )
    font_file_message = random.choice(font_file_message_s)
    return await client.download_media(font_file_message)

CMD_HELP.update({
    "autopp": 
    ".autopp \
    \nİstifadə: Bu əmr göstərdiyiniz fotonu profil şəkli halına gətirir. \
    \nvə bir saat əlavə edir. Bu saat hər dəqiqə dəyişir. \
    \nNOT: K  Qadağan olmağın kiçik bir ehtimalı da var. Buna görə diqqətlə istifadə edin."
})

CMD_HELP.update({
    "autovideo": 
    "`.autovideo` \
    \n**Kullanım:** Bu komut yanıt verdiğiniz videoyu profil video yapar \
    \nve bir saat veya tarih veya istediğiniz bir yazı ekler. Bu saat her dakika değişir. \
    \nEğer botun kendi yazısını kullanmak istiyorsanız ekstradan bir şey yazmayın.\
    \nKendi yazınızı eklemek istiyorsanız .autovideo yazı şeklinde kullanın. \
    \nAyrıca kendi yazınıza `$saat` ve `$tarih` ile saat ve tarih ekleyebilirsiniz. \
    \n\n**Örnek: ** `.autovideo ahan saat $saat bu da tarih $tarih`"
})