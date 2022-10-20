SCRPID=$(./list_screen.sh | grep pybotscreen | cut -d "." -f 1 | sed 's/\t//g')

echo "Switching to : $SCRPID"
echo "Deatch from screen with Ctrl-a, then Ctrl-d"
echo -en "\n\n\n"
echo "*** Using ESC will terminate the bot!***"
echo -en "\n\n\n"
echo "Press ENTER to continue..."

read


screen -r $SCRPID