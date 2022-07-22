# 1/443

from psychopy import visual,core
import numpy, random
from psychopy.hardware import keyboard
kb = keyboard.Keyboard()

numPieces = 60
pieceSize = 100
width = 1536
height = 864


window = visual.Window(fullscr = True)

positionsGratings = (numpy.random.random(size = [numPieces,2]) * 500) - 150
# positionsGratings = numpy.array([[50*(-i+1)*numPiece - 700 * (-i+1) for numPiece in range(numPieces)] for i in range(2)]).T
positionsBars = positionsGratings
# positionsBars = numpy.array([[50*(-i+1)*numPiece - 700 * (-i+1) for numPiece in range(numPieces)] for i in range(2)]).T
# print(positionsBars.shape)
colors = numpy.array([-1,1,-1] * numPieces)
bars = visual.ElementArrayStim(window, nElements = numPieces, elementTex = None, elementMask = None, units = 'pix', sizes = [pieceSize,pieceSize], xys = positionsBars, colors = colors)
n_frameskip = 0
n_trials = 1000
for i in range(n_trials): # 5 trials
    keys = kb.getKeys()
    for thisKey in keys:
        if thisKey=='escape':
            core.quit()
    colors = numpy.array([-1,1,-1] * numPieces)
    trial_text = visual.TextStim(window, 'trial:'+str(i+1)+'/'+str(n_trials), color=(-1, -1, -1), colorSpace='rgb', units='pix', pos=[-200,height/2-50])
    trial_text.size = 50
    for h in range(30): # 30 frames green keys
        # bars = visual.ElementArrayStim(window, nElements = numPieces, elementTex = None, elementMask = None, units = 'pix', sizes = [pieceSize,pieceSize], xys = positionsBars, colors = colors)
        bars.colors = colors
        bars.draw()
        trial_text.draw()
        window.flip()
    for j in range(120): # 120 frames flashing keys
        next_flip = window.getFutureFlipTime()
        # depthGratings = list(range(numPieces))
        # positionsBars = positionsGratings - [.5*pieceSize, 0]
        # positionsRightBar = positionsGratings + [.5*pieceSize, 0]
        # positionsBars = numpy.concatenate((positionsLeftBar, positionsRightBar),axis = 0)
        # depthBars = depthGratings + depthGratings
        colors = [[1,1,1],[-1,-1,-1]] * int(numPieces/2)
        colors2 = numpy.copy(colors)
        colors = numpy.copy(colors2)
        # print(colors.shape)

        random.shuffle(colors)
        colors = numpy.array(colors)
        # bars = visual.ElementArrayStim(window, nElements = numPieces, elementTex = None, elementMask = None, units = 'pix', sizes = [pieceSize,pieceSize], xys = positionsBars, colors = colors)#, depths = depthBars)
        # gratings = visual.ElementArrayStim(window, nElements = numPieces, elementTex = 'sqr', elementMask = None, units = 'pix', sizes = [pieceSize,pieceSize], xys = positionsGratings, colors = [.2,.2,.2], sfs = 4)#, depths = depthGratings)
        bars.colors = colors
        # gratings.draw()
        trial_text.draw()
        bars.draw()
        if core.getTime() > next_flip:
            n_frameskip+=1
            print(str(n_frameskip)+'/'+str(i))
            colors = numpy.array([1,-1,-1] * numPieces)
            for k in range(15): # 15 frames red keys
                # bars = visual.ElementArrayStim(window, nElements = numPieces, elementTex = None, elementMask = None, units = 'pix', sizes = [pieceSize,pieceSize], xys = positionsBars, colors = colors)
                bars.colors = colors
                bars.draw()
                trial_text.draw()
                window.flip()
        window.flip()

# core.wait(5)