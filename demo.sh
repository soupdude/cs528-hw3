#!/bin/bash
URL=$(gcloud functions describe hw3-service1 --gen2 --region=us-central1 --format='value(serviceConfig.uri)')
run() { echo; echo "\$ $*"; "$@" | head -n 12; }
run curl -si "$URL/file_5.txt"                                                   # GET 200
run curl -si -X POST "$URL" -H 'Content-Type: application/json' -d '{"file":"file_5.txt"}'  # POST 200
run curl -si "$URL/nope.txt"                                                     # 404
for m in PUT DELETE PATCH OPTIONS TRACE; do run curl -si -X $m "$URL/file_5.txt"; done   # 501
run curl -sI "$URL/file_5.txt"                                                   # HEAD
for c in "North Korea" Iran Cuba Myanmar Iraq Libya Sudan Zimbabwe Syria; do
  run curl -si -H "X-country: $c" "$URL/file_5.txt"                              # 400
done
run curl -si -H "X-country: Canada" "$URL/file_5.txt"                            # allowed, 200
