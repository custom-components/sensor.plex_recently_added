# plex-recent-media

## Super early version for testing

This is a component to feed the associated Lovelace card: [Upcoming_Media_Card](https://github.com/custom-cards/upcoming-media-card)

**Component:**

    - platform: plex_recent_media
      token: { your plex token }
      host: { IP address }
      port: { port }
      item_count: { Number of recent downloads to show }


**Lovelace:**

    - type: custom:upcoming-media-card
      entity: sensor.plex_recent_media

Set plex server network setting: "Secure connections: Preferred"</br></br>
TV only at the moment

You will get an error about the component taking long to update. Should only happen at first reboot with component.
