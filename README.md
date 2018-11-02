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

* **Need to set "Secure connections" to "Preferred" in Plex network settings**
* **You may get an error about it taking longer than 10 secs to update at the first boot after installing component or if many downloads are reported at once. This is expected, the component needs to save the images from Plex and will normally only do 1-2 at a time. On first boot it saves all images from reported downloads.**
