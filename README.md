# plex_recently_added

## Super early version for testing

This is a component to feed the associated Lovelace card: [Upcoming_Media_Card](https://github.com/custom-cards/upcoming-media-card)

**Component:**

    - platform: plex_recently_added
      token: { your plex token }
      host: { IP address }
      port: { port }
      item_count: { Number of recent downloads to show }


**Lovelace:**

    - type: custom:upcoming-media-card
      entity: sensor.plex_recently_added
