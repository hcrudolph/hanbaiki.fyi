![Django CI Tests](https://github.com/hcrudolph/hanbaiki.fyi/actions/workflows/django.yml/badge.svg)

# HANBAIKI.FYI

[HANBAIKI.FYI](https://hanbaiki.fyi) is part documentary project, part educational exercise. The idea to record and map some of the thousands of vending machines (自動販売機・jidou hanbaiki) in Japan was there for a while. However, there is no way a single person could ever get around to do this on their own. So, I decided to crowdsource it. At the same time, I wanted to toy around with some new technology, including image recognition, that would help with sanitization of people's submissions.

## About this project
This repository contains the source code for the Django project running HANBAIKI.FYI, managing uploading, processing, and display of submitted images. Uploaded photos are processed as follows:

1. Analysis: We read EXIF data embedded into the image by the camera to extract the GPS coordinates of the subject. If those GPS coordinates could be read successfully, processing continues.
2. Recognition: We use image recognition to check if uploaded files indeed contain vending machines. If the confidence score for an image lies above a certain threshold, processing continues.
3. Tagging: We use text recognition to check if uploaded files contain any known Tags (e.g., beverage brands). If the confidence score for a given tag lies above a certain threshold, the tags are automatically associated to the uploaded vending machine.
4. Publication: Processed images are published on our site alongside their GPS coordinates and basic location information, such as state (県・都), city (区・市), postcode (〒), and town (町・村), if available.
