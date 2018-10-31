# plex-recent-media

Super early build for testing

Component:

    - platform: plex_recent_media
      token: { your plex token }
      host: { IP address }
      port: { port }
      item_count: { Number of recent downloads to show }


Lovelace:

    - type: custom:upcoming-media-card
      entity: sensor.plex_recent_media

Set plex server network setting: "Secure connections: Preferred"
TV only at the moment
