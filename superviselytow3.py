import glob, re, os
def tow3(content, metadata, contentmeta):
	annotationbase = {
    "type": "Annotation",
    "@context": "http://www.w3.org/ns/anno.jsonld",
    "label": "",
    "body": [],
    "stylesheet": {
    "type": "CssStylesheet",
    "value": ""
  	},
    "target": {
      "id": "",
      "selector": {}

    }
 	}
	newanno = dict(annotationbase)	
	creator = content['labelerLogin']
	created = content['createdAt']
	modified = content['updatedAt']
	label = contentmeta[content['classId']]['title']
	bodytags = tagstow3(content['tags'], metadata)
	newanno['label'] = label
	newanno['target']['id'] = glob.glob(os.path.join(inputpath, '*.jpg'))[0]
	newanno['body'] = bodytags['tags']
	newanno['target']["styleClass"] = "tag"
	newanno['stylesheet']['value'] = "\n".join(bodytags['classes'])
	if content['geometryType'] == 'polygon':
		polygon = '<svg><polygon points=\"'
		for point in content['points']['exterior']:
			polygon += "{},{} ".format(point[0], point[1])
		polygon = polygon.strip() + '\"></polygon></svg>'
		newanno['target']['selector']['type'] = "SvgSelector"
		newanno['target']['selector']['conformsTo'] = "http://www.w3.org/TR/SVG/"
		newanno['target']['selector']['value'] = polygon
		
	elif content['geometryType'] == 'point':
		newanno['target']['selector']['type'] = "FragmentSelector"
		newanno['target']['selector']['conformsTo'] = "http://www.w3.org/TR/media-frags/"
		newanno['target']['selector']['value'] = "xywh={},{},0,0".format(content['points']['exterior'][0][0], content['points']['exterior'][0][1])
	elif content['geometryType'] == 'line':
		xy = list(content['points']['exterior'][0])
		w = content['points']['exterior'][1][0] - content['points']['exterior'][0][0]
		h = 5
		newanno['target']['selector']['type'] = "FragmentSelector"
		newanno['target']['selector']['conformsTo'] = "http://www.w3.org/TR/media-frags/"
		newanno['target']['selector']['value'] = "xywh={},{},{},{}".format(xy[0],xy[1],w,h)
	else:
		print(content['geometryType'])
		return None
	if len(bodytags['tags']) > 0:
		return newanno
	else:
		return None

def tagstow3(tags, metadata):
	tagslist = []
	classes = []
	for tag in tags:
		value = str(tag['value'])
		group = str(tag['name'])
		if value != 'None' or group != 'None':
			group = group.replace('*', '').replace('?', '').strip()
			if value != 'None' and group != 'None':
				tagdataset= {'group': group, 'value': value}
				tagtype = 'Dataset'
			else:
				tagtype = 'TextualBody'
				tagdataset = value if value != 'None' else group
			tagdict = {
				'value': tagdataset,
				'creator': tag['labelerLogin'],
				'created': tag['createdAt'],
				'modified': tag['updatedAt'],
				'purpose':'tagging',
				'type': tagtype
			}
			try:
				tagidfield = tag['tagId'] if 'tagId' in tag.keys() else tag['id']
				color = metadata[tagidfield]
				classes.append(".tag .%s {\ncolor: %s\n}\n"%(tagtoclass(group), color))
			except:
				print('no color')
			tagslist.append(tagdict)
	return {'classes': classes, 'tags': tagslist}

def tagtoclass(group):
	regex = r"-?[_a-zA-Z]+[_a-zA-Z0-9-]*"
	return "".join(re.findall(regex, ".{}".format(group.lower())))

import json
inputpath = input("Enterfilepath to contents: ")
meta = glob.glob(os.path.join(inputpath, "meta.json"))
with open(meta[0], "r") as read_file:
    metadata = json.load(read_file)
file = glob.glob(os.path.join(inputpath, "*.jpg.json"))

with open(file[0], "r") as read_file:
    contents = json.load(read_file)
parsemeta = {}
contentmeta = {}
for meta in metadata['tags']:
	parsemeta[meta['id']] = meta['color']
for metaclass in metadata['classes']:
 	contentmeta[metaclass['id']] = metaclass
keys = []
resources = []
for content in contents['objects']:
	for key in content.keys():
		if key not in keys:
			keys.append(key)
	annotation = tow3(content, parsemeta, contentmeta)
	
	if annotation != None:
		resources.append(annotation)
with open('{}-w3annotation.json'.format(os.path.basename(inputpath)), 'w') as output:
	listanno = {"@context": "http://www.w3.org/ns/anno.jsonld", "type": "AnnotationPage", "items": list(resources)}
	output.write(json.dumps(listanno))


