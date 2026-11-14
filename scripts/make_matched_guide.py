"""Build an XMLTV feed with provider aliases. Contains no provider credentials."""
import copy, datetime, gzip, json, pathlib, xml.etree.ElementTree as ET

rules = json.loads(pathlib.Path('channel-aliases.json').read_text())
root = ET.fromstring(gzip.decompress(pathlib.Path('guide.xml.gz').read_bytes()))
channels = {c.get('id'): c for c in root.findall('channel')}
programmes = {}
for p in root.findall('programme'):
    programmes.setdefault(p.get('channel'), []).append(p)
now = datetime.datetime.now(datetime.timezone.utc)
output = ET.Element('tv', {'generator-info-name': 'iptv-org EPG with channel aliases'})
used = set(); total = 0; fresh_channels = 0
for source, rule in rules.items():
    if source not in channels or not programmes.get(source):
        continue
    fresh = any(datetime.datetime.strptime(p.get('stop'), '%Y%m%d%H%M%S %z') > now for p in programmes[source])
    for target in [source] + rule['aliases']:
        if target in used:
            raise ValueError('Duplicate XMLTV ID: ' + target)
        used.add(target)
        c = copy.deepcopy(channels[source]); c.set('id', target)
        existing = {n.text for n in c.findall('display-name')}
        for name in rule['names']:
            if name not in existing:
                ET.SubElement(c, 'display-name').text = name
                existing.add(name)
        output.append(c)
        fresh_channels += int(fresh)
for source, rule in rules.items():
    if source not in channels or not programmes.get(source):
        continue
    for target in [source] + rule['aliases']:
        for p in programmes[source]:
            p = copy.deepcopy(p); p.set('channel', target); output.append(p); total += 1
assert fresh_channels >= 100 and total >= 1000, 'Matched source has insufficient current listings'
with gzip.open('guide-matched.xml.gz', 'wb') as f:
    f.write(ET.tostring(output, encoding='utf-8', xml_declaration=True))
status = {'updated_utc': now.isoformat(), 'xmltv_channel_entries': len(used), 'entries_with_upcoming_listings': fresh_channels,
          'programmes': total, 'provider_aliases_configured': sum(len(v['aliases']) for v in rules.values()),
          'source_channels_configured': len(rules)}
pathlib.Path('status-matched.json').write_text(json.dumps(status, indent=2) + '\n')
print(json.dumps(status, indent=2))
