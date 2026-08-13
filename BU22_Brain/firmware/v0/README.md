# BU-22 Brain firmware v0 exerciser

This is a temporary controller for validating the first clean Eyes wire-protocol
slice. It cycles stored expressions and animations, interrupts an animation,
tests Off/Normal, requests missing animation ID `999`, reads its visible error
status, and recovers with Normal.
