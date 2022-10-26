#screen -L -S pybotscreen -dm ./pybot.py 

echo -en "\n\nStarting bot in screen"
echo -en "\n\nUse ctrl-a then ctr-d to send it to background"
echo -en "\n\nRecall running bot from background with:\n"
echo "./switch_to_screen.sh"

read

screen -L -A -S pybotscreen  ./pybot.py