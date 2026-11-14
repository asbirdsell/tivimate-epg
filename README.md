# TiviMate EPG

A daily XMLTV guide generated with [iptv-org/epg](https://github.com/iptv-org/epg), covering a selection of 2,345 Canadian, US and UK guide entries (573 Canadian, 1,445 US, 322 UK, and 5 legacy entries). Coverage depends on the upstream schedule sources; not every selected channel is guaranteed to return listings.

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
- Entries without an upstream XMLTV ID use a stable `TVPassport-<station-number>` or `TVPassport-<station-number>.ca` ID and generally need manual assignment.
- Sources currently used: TV Passport, TV Guide, TV Hebdo and Sky. Source availability and regional schedules may vary.

## Automatic ID matching

A smaller feed with provider-compatible XMLTV IDs and channel-name aliases is published at:

```text
https://raw.githubusercontent.com/asbirdsell/tivimate-epg/main/guide-matched.xml.gz
```

The `Publish matched TV guide` workflow runs after every successful daily source refresh. `status-matched.json` records its publication status. The rules contain channel identifiers and names only; account credentials and stream URLs are not stored in this repository.

Provider IDs shared by different regional feeds cannot uniquely identify both schedules. A corrected private M3U playlist can assign the canonical IDs per channel. Blank IDs also require playlist correction when the player cannot match a display name.

## Gap coverage

The matched feed now loads the main and supplemental daily XMLTV schedules. `channel-matches.json.gz.b64` contains compressed, credential-free matching rules. Exact names, callsigns and network aliases are preferred. Alternate regional/network feeds and shifted schedules are labelled approximate in programme descriptions.

Channels without published schedules receive explicit 24/7, event-channel or schedule-unavailable blocks rather than fabricated programme listings. These blocks identify the channel; they do not assert a current episode or live event. Provider IDs reused for multiple channels can still require a corrected private M3U playlist for unique per-channel assignment. Channel-name aliases are included for players supporting name matching.

Supplemental sources refresh daily via `Refresh extra channel guides`, and successful main or supplemental downloads rebuild the matched feed. See `status-matched.json` for actual coverage by type and region.
