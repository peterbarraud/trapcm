import winsound


def beeper(repeat : int =1, hertz : int = 1000, duration : int =1000):
    '''
        Set repeat to how many times you want it to beep-beep-beep
        Set frequency to hertz
        Set duration to how long a single beep lasts
        duration = 
    '''
    for _ in range(repeat):
        winsound.Beep(hertz, duration)


if __name__ == '__main__':
    beeper(2)
    