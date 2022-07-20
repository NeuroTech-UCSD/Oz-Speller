from psychopy import visual,core
import numpy, random


numPieces = 60
pieceSize = 100



window = visual.Window(fullscr = True)

# positionsGratings = (numpy.random.random(size = [numPieces,2]) * 500) - 150
# positionsGratings = numpy.array([[50*(-i+1)*numPiece - 700 * (-i+1) for numPiece in range(numPieces)] for i in range(2)]).T
# positionsBars = positionsGratings
positionsBars = numpy.array([[50*(-i+1)*numPiece - 700 * (-i+1) for numPiece in range(numPieces)] for i in range(2)]).T
print(positionsBars.shape)
colors = numpy.array([-1,1,-1] * numPieces)
bars = visual.ElementArrayStim(window, nElements = numPieces, elementTex = None, elementMask = None, units = 'pix', sizes = [pieceSize,pieceSize], xys = positionsBars, colors = colors)

for i in range(5): # 5 trials
    colors = numpy.array([-1,1,-1] * numPieces)
    for h in range(30): # 30 frames green keys
        # bars = visual.ElementArrayStim(window, nElements = numPieces, elementTex = None, elementMask = None, units = 'pix', sizes = [pieceSize,pieceSize], xys = positionsBars, colors = colors)
        bars.colors = colors
        bars.draw()
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
        bars.draw()
        if core.getTime() > next_flip:
            colors = numpy.array([1,-1,-1] * numPieces)
            for k in range(15): # 15 frames red keys
                # bars = visual.ElementArrayStim(window, nElements = numPieces, elementTex = None, elementMask = None, units = 'pix', sizes = [pieceSize,pieceSize], xys = positionsBars, colors = colors)
                bars.colors = colors
                bars.draw()
                window.flip()
        window.flip()

# core.wait(5)