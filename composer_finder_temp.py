
# coding: utf-8

# In[10]:

import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from music21 import *
import music21    


# In[11]:

from nupic.encoders.scalar import ScalarEncoder
from nupic.research.spatial_pooler import SpatialPooler
from nupic.research.TP import TP


# In[12]:

score = converter.parse('/Users/u608/Downloads/beethoven/pathet1.mid')
#score = converter.parse('/Users/u608/Downloads/taylorswift/taylor_swift-fearless.mid')


# In[13]:

partStream = score.parts
#print partStream.getContextByClass('TimeSignature')
#print partStream.getContextByClass('KeySignature')

storage_list = [-1] * 10000
i = 0
for p in partStream:
    for note in p.flat.notesAndRests:
        #pitch_val = -1

        if isinstance(note, music21.chord.Chord):
            pitch_val = note.root().midi
        elif isinstance(note, music21.note.Note):
            pitch_val = note.pitch.midi
        else: #rest
            continue
            #pass
        storage_list[i] = pitch_val
        i += 1

        # This will fill upcoming portions of the list, 
        # but may be over written again later on.
        #for i in range(int(note.duration.quarterLength * 12)):
        #    storage_list[int(12 * note.offset) + i] = pitch_val


# In[14]:

def convert_note(x):
    fifth_list = [0,7,2,9,4,11,6,1,8,3,10,5] * 2
    if x == -1:
        return 12
    else:
        return fifth_list[x%24]

converted_list = map(convert_note, storage_list)


# In[16]:

enc = ScalarEncoder(n=24, w=3, minval=0, maxval=23, clipInput=True, forced=True)

encoded_list = map(enc.encode, converted_list)

print 'STARTING SPATIAL POOLING'

# In[17]:

sp = SpatialPooler(inputDimensions=(24,),
                   columnDimensions=(4,),
                   potentialRadius=15,
                   numActiveColumnsPerInhArea=1,
                   globalInhibition=True,
                   synPermActiveInc=0.03,
                   potentialPct=1.0)


# In[18]:

for column in xrange(4):
    connected = np.zeros((24,), dtype="int")
    sp.getConnectedSynapses(column, connected)
    print connected


# In[19]:

output = np.zeros((4,), dtype="int")
for _ in xrange(20):
    print 'iteration #' + str(_)
    for note in encoded_list:
        sp.compute(note, learn=True, activeArray=output)

print 'FINISHED SPATIAL POOLING'

# In[20]:

for column in xrange(4):
    connected = np.zeros((24,), dtype="int")
    sp.getConnectedSynapses(column, connected)
    print connected


print 'STARTING TEMPORAL POOLING'

# In[21]:

tp = TP(numberOfCols=50, cellsPerColumn=2,
        initialPerm=0.5, connectedPerm=0.5,
        minThreshold=10, newSynapseCount=10,
        permanenceInc=0.1, permanenceDec=0.0,
        activationThreshold=8,
        globalDecay=0, burnIn=1,
        checkSynapseConsistency=False,
        pamLength=10)


# In[22]:

for i in range(1):
    for note in encoded_list:
        tp.compute(note, enableLearn = True, computeInfOutput = False)
        # This function prints the segments associated with every cell.$$$$
        # If you really want to understand the TP, uncomment this line. By following
        # every step you can get an excellent understanding for exactly how the TP
        # learns.
        # tp.printCells()
    tp.reset()


print 'FINISHED TEMPORAL POOLING'

# In[ ]:

def formatRow(x):
    s = ''
    for c in range(len(x)):
        if c > 0 and c % 10 == 0:
            s += ' '
        s += str(x[c])
    s += ' '
    return s


# In[ ]:

for note in encoded_list:
    print "Raw input vector\n", formatRow(note)

    # Send each vector to the TP, with learning turned off
    tp.compute(note, enableLearn=False, computeInfOutput=True)

    # This method prints out the active state of each cell followed by the
    # predicted state of each cell. For convenience the cells are grouped
    # 10 at a time. When there are multiple cells per column the printout
    # is arranged so the cells in a column are stacked together
    #
    # What you should notice is that the columns where active state is 1
    # represent the SDR for the current input pattern and the columns where
    # predicted state is 1 represent the SDR for the next expected pattern
    print "\nAll the active and predicted cells:"
    tp.printStates(printPrevious=False, printLearnState=False)

    # tp.getPredictedState() gets the predicted cells.
    # predictedCells[c][i] represents the state of the i'th cell in the c'th
    # column. To see if a column is predicted, we can simply take the OR
    # across all the cells in that column. In numpy we can do this by taking
    # the max along axis 1.
    print "\n\nThe following columns are predicted by the temporal pooler. This"
    print "should correspond to columns in the *next* item in the sequence."
    predictedCells = tp.getPredictedState()
    print formatRow(predictedCells.max(axis=1).nonzero())


# In[ ]:



