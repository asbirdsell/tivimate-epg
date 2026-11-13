# TiviMate EPG

A daily XMLTV guide generated with [iptv-org/epg](https://github.com/iptv-org/epg), covering a starting selection of 269 Canadian and US channels. Coverage depends on the upstream schedule sources; not every selected channel is guaranteed to return listings.

## EPG URL

```text
https://raw.githubusercontent.com/asbirdsell/tivimate-epg/main/guide.xml.gz
```

Uncompressed alternative:

```text
https://raw.githubusercontent.com/asbirdsell/tivimate-epg/main/guide.xml
```

These addresses work once the first successful workflow publishes the guide.

## TiviMate setup

1. Open Settings → EPG → EPG sources → Add source.
2. Enter the URL above and save.
3. Open Settings → Playlists → your playlist → EPG sources, and enable the new source.
4. Open Settings → EPG → Update EPG.
5. For unmatched channels, open the channel's options → Assign EPG, then search for the channel name. Channel IDs must match your playlist for automatic assignment.

This repository supplies programme listings only, not TV streams.

## Refresh

The workflow runs daily at 10:23 UTC (5:23 a.m. Toronto standard time / 6:23 a.m. daylight time), requests three days of listings, and can also be run manually from Actions → Refresh TV guide → Run workflow.

GitHub scheduled runs can be delayed. GitHub may disable scheduled workflows in public repositories after 60 days without repository activity; check Actions if updates stop.

`status.json` records the last successful publication and actual channel/programme coverage. If a refresh fails validation, the last successfully published guide is preserved, but it will eventually become stale.

## Maintenance

- Edit `channels.xml` to change the channel selection.
- The generator is pinned to upstream commit `6a74973f1e0657184bf168e589a043ac66bac551`. Review upstream changes and update the workflow pin when sources change.
- Entries without an upstream XMLTV ID use a stable `TVPassport-<station-number>` ID and generally need manual assignment.
- Sources currently used: TV Passport and TV Guide. Source availability and regional schedules may vary.
