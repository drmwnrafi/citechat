# import pygame

# #Instantiate mixer
# pygame.init()

# #Load audio file
# ply = pygame.mixer.Sound('/home/ziczac/dev/citechat/speech.ogg')

# #Play the music
# ply.play()

# #Infinite loop
# while True:
# 	print("------------------------------------------------------------------------------------")
# 	print("Press 'p' to pause the music")
# 	print("Press 'r' to resume the music")
# 	print("Press 'e' to exit the program")

# 	#take user input
# 	userInput = input(" ")
	
# 	if userInput == 'p':

# 		# Pause the music
# 		pygame.mixer.pause()	
# 		print("music is paused....")
# 	elif userInput == 'r':

# 		# Resume the music
# 		pygame.mixer.unpause()
# 		print("music is resumed....")
# 	elif userInput == 'e':

# 		# Stop the music playback
# 		pygame.mixer.stop()
# 		print("music is stopped....")
# 		break

import speech_recognition as sr

r = sr.Recognizer()

# open the file
with sr.AudioFile("/home/ziczac/dev/citechat/speech_1.wav") as source:
    # listen for the data (load audio to memory)
    audio_data = r.record(source)
    # recognize (convert from speech to text)
    text = r.recognize_google(audio_data)
    print(text)