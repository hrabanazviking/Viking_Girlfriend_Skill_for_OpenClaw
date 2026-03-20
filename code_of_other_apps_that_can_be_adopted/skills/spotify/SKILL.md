---
name: spotify
description: Control Spotify playback, search tracks/albums/playlists, and manage queues via the Spotify Web API.
always: false
script: spotify
requirements: {"env":["SPOTIFY_CLIENT_ID","SPOTIFY_CLIENT_SECRET"]}
metadata: {"clawlite":{"emoji":"🎵","auth":{"requiredEnv":["SPOTIFY_CLIENT_ID","SPOTIFY_CLIENT_SECRET"],"optionalEnv":["SPOTIFY_ACCESS_TOKEN"]}}}
---

# Spotify

Use this skill when the user wants to control Spotify playback or search for music.

## Auth

Spotify Web API requires OAuth 2.0. Set:
- `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` (from https://developer.spotify.com/dashboard)
- `SPOTIFY_ACCESS_TOKEN` (short-lived; refresh with refresh token as needed)

Alternatively use `spotify-player` CLI if installed: `spotify_player` command.

## Base URL

```
https://api.spotify.com/v1
Headers: Authorization: Bearer $SPOTIFY_ACCESS_TOKEN
```

## Key endpoints

```
GET  /me/player                        # current playback state
PUT  /me/player/play                   # resume/start playback
PUT  /me/player/pause                  # pause
POST /me/player/next                   # skip to next track
POST /me/player/previous               # skip to previous
PUT  /me/player/volume?volume_percent=N
GET  /search?q=QUERY&type=track,album,playlist&limit=10
GET  /tracks/{track_id}
GET  /albums/{album_id}
GET  /playlists/{playlist_id}
POST /me/player/queue?uri=spotify:track:ID  # add to queue
GET  /me/playlists                     # user's playlists
GET  /me/top/tracks?time_range=medium_term
```

## spotify-player CLI (if available)

```bash
spotify_player playback play
spotify_player playback pause
spotify_player playback next
spotify_player search --query "artist:Radiohead"
```

## Safety notes

- Playback commands require an active Spotify Premium device.
- Token expiry is 1 hour; handle 401 by refreshing.
