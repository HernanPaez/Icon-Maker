import os
import uuid
import json
import zipfile
from PIL import Image
import config

class SizeItem:
    size = (0, 0)
    scale = 1

    def __init__(self, size, scale):
        self.size = size
        self.scale = scale

    def map(self):
        data = {}

        if isinstance(self.size[0], float) and isinstance(self.size[1], float):
            data['size'] = "%.1fx%.1f" % (self.size[0], self.size[1])
        else:
            data['size'] = "%dx%d" % (self.size[0], self.size[1])

        data['filename'] = self.filename()
        data['scale'] = "%dx" % (self.scale)

        return data

    def final_size(self):
        return (int(self.size[0] * self.scale), int(self.size[1] * self.scale))

    def filename(self):
        return "%dx%d@%dx.png" % (self.size[0], self.size[1], self.scale)

class IOS_Marketing_Size(SizeItem):
    def filename(self):
        return config.ITUNES_ARTWORK_NAME

    def map(self):
        data = SizeItem.map(self)
        data['idiom'] = 'ios-marketing'
        return data

class IPad_Size(SizeItem):
    def filename(self):
        return "iPad-" + SizeItem.filename(self)

    def map(self):
        data = SizeItem.map(self)
        data['idiom'] = 'ipad'
        return data

class IPhoneSize(SizeItem):
    def filename(self):
        return "iPhone-" + SizeItem.filename(self)

    def map(self):
        data = SizeItem.map(self)
        data['idiom'] = 'iphone'
        return data


IOS_SIZES = [IPhoneSize((20,20), 2), IPhoneSize((20,20), 3), IPhoneSize((29,29), 2), IPhoneSize((29,29), 3), IPhoneSize((40,40), 2), IPhoneSize((40,40), 3), IPhoneSize((60,60), 2), IPhoneSize((60,60), 3), IOS_Marketing_Size((1024, 1024), 1)]
IPAD_SIZES = [IPad_Size((20,20), 1), IPad_Size((20,20), 2), IPad_Size((29,29), 1), IPad_Size((29,29), 2), IPad_Size((40,40), 1), IPad_Size((40,40), 2), IPad_Size((76,76), 1) ,IPad_Size((76,76), 2), IPad_Size((83.5,83.5), 2)]

def resize(file):
    image = Image.open(file)
    icon_id = str(uuid.uuid4())
    path = os.path.join(config.UPLOAD_FOLDER, icon_id)
    os.makedirs(path)

    map_arr = []
    zip_path = os.path.join(path, config.IOS_APPICONSET_NAME)
    zf = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
    
    #Resize iPhone Size
    for t in IOS_SIZES:
        out = image.resize(t.final_size(), resample=Image.LANCZOS)
        filepath = os.path.join(path, t.filename())
        out.save(filepath)
        map_arr.append(t.map())

        zf.write(filepath, t.filename())
        os.remove(filepath)

    #Resize iPad Size
    for t in IPAD_SIZES:
        
        out = image.resize(t.final_size(), resample=Image.LANCZOS)
        filepath = os.path.join(path, t.filename())
        out.save(filepath)
        map_arr.append(t.map())

        zf.write(filepath, t.filename())
        os.remove(filepath)

    #Save Appstore Size
    itunes_filename = config.ITUNES_ARTWORK_NAME
    appstore_image = image.resize((1024, 1024), resample=Image.LANCZOS)
    appstore_file_path = os.path.join(path, itunes_filename)
    appstore_image.save(appstore_file_path)
    zf.write(appstore_file_path, itunes_filename)

    #Create Contents.json
    json_filename = 'Contents.json'
    json_data = json.dumps({'images' : map_arr, 'info' : {'version' : 1, 'author' : 'hernan'}}, sort_keys=True, indent=4)

    json_filepath = os.path.join(path, json_filename)
    json_file = open(json_filepath, 'w')
    json_file.write(json_data)
    json_file.close()

    zf.write(json_filepath, json_filename)
    os.remove(json_filepath)

    zf.close()
    return icon_id
