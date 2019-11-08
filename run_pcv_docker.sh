#!/bin/bash
# Basic while loop
counter=10
while [ $counter -le 1000 ]
do
echo $counter

docker run -v "$PWD":/home/joyvan/pcv -v "$HOME"/.ssh/:/home/joyvan/.ssh 6d2ca9b5f7e2 python /home/joyvan/pcv/02-analyse-image.py $counter
((counter++))
done
echo All done