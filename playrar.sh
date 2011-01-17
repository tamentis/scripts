#!/bin/ksh
#
# This script is used to play a movie out of a series of RAR files. This is
# particularily useful when downloading a movie in the right order since it
# allows you to start watching the movie almost as soon as you start your
# download.
#

if [ -z "$*" ]; then
	echo "usage: playrar movie.part01.rar"
	exit
fi

RAR=`which rar`
if [ -z "$RAR" ]; then
	echo "rar was not found (aptitude install rar)"
	exit
fi

MPLAYER=`which mplayer`
if [ -z "$MPLAYER" ]; then
	echo "mplayer was not found (aptitude install mplayer)"
	exit
fi

FILENAME=`$RAR l "$*" | grep '\(avi\|mkv\)' | sed 's/^\s*//;s/\.\(\w\w\w\)\s.*/\.\1/'`

if [ -z "$FILENAME" ]; then
	echo "Unable to find an avi or mkv file."
	exit
fi

echo "Detected $FILENAME"

# Extract the selected file to a fifo
mkfifo "$FILENAME"
$RAR e -o+ "$*" &
UNRAR_PID=$!

# Pipe to mplayer
$MPLAYER "$FILENAME"

# Cleanup
kill $UNRAR_PID
rm -f "$FILENAME"

