import dbus
import tempfile
import os
from PIL import Image


def screenshot_via_portal(x, y, width, height, output_path="screenshot.png"):
    bus = dbus.SessionBus()
    portal = bus.get_object('org.freedesktop.portal.Desktop',
                            '/org/freedesktop/portal/desktop')
    
    token = 'screenshot_token'
    reply = portal.Screenshot(
        '',
        {
            'handle_token': dbus.String(token),
            'interactive': dbus.Boolean(False)
        },
        dbus_interface='org.freedesktop.portal.Screenshot'
    )

    uri = str(reply.get('uri'))
    if uri.startswith('file://'):
        temp_path = uri[7:]  # Убираем 'file://' из начала строки
    
    # 2. Открываем, обрезаем и сохраняем
    if temp_path and os.path.exists(temp_path):
        im = Image.open(temp_path)
        cropped_im = im.crop((x, y, x + width, y + height))
        cropped_im.save(output_path)
        print(f"Скриншот сохранён: {output_path}")
        
        # Удаляем временный файл
        os.unlink(temp_path)
    else:
        print("Не удалось получить путь к временному файлу скриншота.")

screenshot_via_portal(100, 100, 800, 600, 'my_wayland_shot.png')
