#!/bin/sh
gst-launch-1.0 -v udpsrc port=9999 caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! avdec_h264 ! queue ! videoconvert ! autovideosink
