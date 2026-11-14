"""Build provider-compatible XMLTV with real, approximate and labelled gap data."""
import base64,collections,copy,datetime,gzip,json,pathlib
import xml.etree.ElementTree as E
from xml.sax.saxutils import quoteattr
now=datetime.datetime.now(datetime.timezone.utc)
channels={};programmes=collections.defaultdict(list);loaded=0
for file in ['guide.xml.gz','guide-extra.xml.gz']:
 if pathlib.Path(file).exists():
  r=E.fromstring(gzip.decompress(pathlib.Path(file).read_bytes()));loaded+=1
  for c in r.findall('channel'):channels[c.get('id')]=c
  for p in r.findall('programme'):programmes[p.get('channel')].append(p)
def date(s):return datetime.datetime.strptime(s,'%Y%m%d%H%M%S %z')
fresh={k for k,v in programmes.items() if any(date(p.get('stop'))>now for p in v)}
f=pathlib.Path('channel-matches.json.gz.b64')
if f.exists():rules=json.loads(gzip.decompress(base64.b64decode(f.read_bytes())))['entries']
else:
 rules=[]
 for source,v in json.loads(pathlib.Path('channel-aliases.json').read_text()).items():
  for target in [source]+v['aliases']:rules.append(dict(id=target,source=source,names=v['names'],kind='schedule',title=v['names'][0]))
selected=[];used=set();counts=collections.Counter();regions=collections.defaultdict(collections.Counter)
for raw in rules:
 x=dict(raw);target=x['id']
 if target in used:raise ValueError('Duplicate channel ID')
 used.add(target);source=x.get('source')
 if source not in fresh:
  source=x.get('fallback_source')
  if source in fresh:x['approximate']=True
  else:source=None
 x['selected_source']=source
 kind=('approximate' if x.get('approximate') else 'schedule') if source else x.get('kind','unavailable')
 if not source and kind=='schedule':kind='unavailable'
 x['output_kind']=kind;counts[kind]+=1
 if target.startswith('name-'):regions[x.get('region','other')][kind]+=1
 selected.append(x)
for source in sorted({x['selected_source'] for x in selected if x['selected_source']}):
 if source not in used:selected.append(dict(id=source,selected_source=source,names=[],output_kind='schedule',title=source));used.add(source)
cache={};total=0
def real(x):
 source=x['selected_source'];shift=int(x.get('shift_minutes',0));approx=bool(x.get('approximate'));key=(source,shift,approx)
 if key not in cache:
  data=[];label=channels[source].findtext('display-name') or source
  for original in programmes[source]:
   if not approx and not shift:data.append(E.tostring(original,encoding='utf-8'));continue
   p=copy.deepcopy(original)
   if shift:
    for attr in ['start','stop']:p.set(attr,(date(p.get(attr))+datetime.timedelta(minutes=shift)).strftime('%Y%m%d%H%M%S %z'))
   if approx:
    d=p.find('desc')
    if d is None:d=E.SubElement(p,'desc')
    d.text=(d.text+'\n\n' if d.text else '')+'Approximate schedule from '+label+'. Regional programmes or timing may differ.'
   data.append(E.tostring(p,encoding='utf-8'))
  cache[key]=data
 before=('channel='+quoteattr(source)).encode();after=('channel='+quoteattr(x['id'])).encode()
 for b in cache[key]:yield b.replace(before,after,1)
def gap(x):
 kind=x['output_kind'];label=x.get('title') or x['names'][0]
 suffix={'continuous':'24/7 channel','event':'Event channel','unavailable':'Schedule unavailable'}.get(kind,'Schedule unavailable')
 desc={'continuous':'Continuous or on-demand-style channel. Individual episode titles and start times are not supplied.','event':'Event listings are not supplied. Check the broadcast for the event and start time.','unavailable':'No verified programme schedule is available for this feed. This block identifies the channel only.'}.get(kind,'No verified programme schedule is available.')
 start=now.replace(minute=0,second=0,microsecond=0)-datetime.timedelta(hours=1)
 for i in range(13):
  a=start+datetime.timedelta(hours=6*i);b=a+datetime.timedelta(hours=6)
  p=E.Element('programme',{'channel':x['id'],'start':a.strftime('%Y%m%d%H%M%S %z'),'stop':b.strftime('%Y%m%d%H%M%S %z')})
  E.SubElement(p,'title').text=label+' — '+suffix;E.SubElement(p,'desc').text=desc
  yield E.tostring(p,encoding='utf-8')
with gzip.open('guide-matched.xml.gz','wb',compresslevel=6) as f:
 f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="iptv-org with provider matching">\n')
 for x in selected:
  source=x['selected_source'];c=E.Element('channel',{'id':x['id']})
  names=x['names'] or ([channels[source].findtext('display-name')] if source else [x.get('title',x['id'])])
  for name in dict.fromkeys(names):E.SubElement(c,'display-name').text=name
  if source:
   icon=channels[source].find('icon')
   if icon is not None:c.append(copy.deepcopy(icon))
  f.write(E.tostring(c,encoding='utf-8')+b'\n')
 for x in selected:
  for b in (real(x) if x['selected_source'] else gap(x)):f.write(b+b'\n');total+=1
 f.write(b'</tv>\n')
assert counts['schedule']+counts['approximate']>=100,'Real guide data unavailable'
status={'updated_utc':now.isoformat(),'xmltv_channel_entries':len(used),'programmes':total,'matched_entry_types':dict(counts),'channel_name_coverage_by_region':{k:dict(v) for k,v in regions.items()},'real_source_channels':len(fresh),'supplemental_source_present':loaded>1}
pathlib.Path('status-matched.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status,indent=2))
